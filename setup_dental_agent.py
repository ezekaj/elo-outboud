import os
import subprocess
import torch
from huggingface_hub import snapshot_download, login
from tqdm import tqdm

def setup_environment():
    """Install necessary packages for dental outbound calling agent"""
    required_packages = [
        "transformers>=4.38.0",
        "accelerate>=0.27.0",
        "bitsandbytes>=0.41.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "peft>=0.7.0",
        "huggingface_hub>=0.19.0",
        "tqdm",
        "sentencepiece",
        "protobuf"
    ]
    
    print("Installing required packages...")
    for package in required_packages:
        try:
            subprocess.check_call(["pip", "install", "-U", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
    
    print("✅ Environment setup complete")

def check_gpu_compatibility():
    """Check if the GPU is compatible with the model"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU detected: {gpu_name} with {vram_gb:.2f} GB VRAM")
        
        if vram_gb >= 16:
            print("✅ Your GPU has sufficient VRAM for running the dental outbound agent")
            return True
        else:
            print("⚠️ Your GPU has limited VRAM. Will configure for low-memory usage.")
            return True
    else:
        print("❌ No GPU detected. Model download will proceed but inference may be slow.")
        return False

def authenticate_huggingface():
    """Authenticate with Hugging Face"""
    print("\n" + "=" * 50)
    print("HUGGING FACE AUTHENTICATION")
    print("=" * 50)
    print("You need to authenticate with Hugging Face to download Llama 3.1")
    print("Please visit: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct")
    print("Accept the license agreement, then get your token from: https://huggingface.co/settings/tokens")
    
    token = input("Enter your Hugging Face token: ")
    if token.strip():
        login(token=token)
        return True
    else:
        print("No token provided. Will attempt to use existing credentials if available.")
        return False

def download_llama3_1():
    """Download Llama 3.1 model from Hugging Face"""
    # Create directory for the model
    base_dir = "models"
    model_dir = os.path.join(base_dir, "llama-3.1-8b-dental")
    os.makedirs(model_dir, exist_ok=True)
    print(f"Created directory: {model_dir}")
    
    # Model ID for Llama 3.1
    model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    
    print("\n" + "=" * 50)
    print("DOWNLOADING LLAMA 3.1 8B INSTRUCT MODEL FOR DENTAL OUTBOUND CALLING")
    print("=" * 50)
    
    try:
        print(f"Downloading {model_id} to {model_dir}...")
        snapshot_download(
            repo_id=model_id,
            local_dir=model_dir,
            ignore_patterns=["*.safetensors", "*.bin"] if torch.cuda.is_available() else ["*.safetensors"],
        )
        print(f"✅ Successfully downloaded {model_id}")
        return model_dir
    except Exception as e:
        print(f"❌ Error downloading Llama 3.1: {e}")
        print("\nPossible reasons for failure:")
        print(f"1. You need to accept the license agreement at https://huggingface.co/{model_id}")
        print("2. Your Hugging Face token may not have the necessary permissions")
        print("3. There might be network connectivity issues")
        
        return None

def create_dental_agent_script(model_dir):
    """Create a dental outbound calling agent script using the downloaded model"""
    script_path = os.path.join(os.path.dirname(model_dir), "dental_outbound_agent.py")
    
    script_content = f"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import datetime

# Load the dental agent instructions
AGENT_INSTRUCTION = \"\"\"
# Persona
You are Elo, a warm and professional AI assistant for Romi Dental Clinic. Your goal is to understand clients' dental needs and help them take the next step toward better oral health. You speak English with empathy and expertise.

# Core Approach: LISTEN → UNDERSTAND → HELP
1. **Listen First**: Ask about their dental situation and concerns
2. **Understand Needs**: Identify their specific pain points and goals
3. **Help Appropriately**: Offer relevant solutions and next steps

# Key Principles
- **Empathy**: Acknowledge their feelings and time constraints
- **Respect**: Never pressure; offer to reschedule if they're busy
- **Value**: Focus on health benefits, not sales
- **Simplicity**: Keep responses concise (2-3 sentences max)

# Handling Common Responses

## "Not Interested"
- Use light humor: "I get it - another call! But this is free dental health info that could save you money and pain later."
- Emphasize value: "Our patients say we're like a spa day for their teeth, with amazing results!"
- Create curiosity: "What if I told you we could give you a smile you'd be proud to show off?"

## "I'm Busy"
- "I completely understand. When would be a better time to call you back?"
- "No problem at all. Should I try calling you [alternative time]?"
- "Would you prefer if I sent you some information via text instead?"

## High Interest Clients
- Focus on detailed consultation and immediate booking
- "Based on what you've shared, I think we can really help you with this."

## Low Interest Clients
- Be efficient but professional
- "I understand. Thank you for your time. We're here if you ever need dental care."

# Services We Offer
- Regular check-ups and cleanings
- Cosmetic dentistry and whitening
- Emergency dental care
- Children's dentistry
- Dental implants and prosthetics

# Payment Policy
- All payments made at clinic in Euro for security
- We accept cash, credit cards, and bank transfers
- Never process payments over the phone
- Consultation fees payable when you visit

# Sample Conversation Flow
1. **Opening**: "Good morning! I'm Elo from Romi Dental Clinic. I'm reaching out to understand how we can help with your dental health. How long has it been since your last check-up?"

2. **Understanding**: Listen to their response, ask follow-up questions about concerns or goals

3. **Educating**: "Regular dental care can save you thousands in the long run and prevent serious issues."

4. **Converting**: "Would you like to schedule a consultation to discuss this further? We have special offers for new patients."

Remember: Be genuine, respectful, and focused on their health needs. Your name is Elo, and you represent a caring medical facility.
\"\"\"

# Configure 4-bit quantization for efficient inference
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Path to the downloaded model
model_path = "{model_dir}"

# Load tokenizer and model
print("Loading Llama 3.1 8B Instruct tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("Loading Llama 3.1 8B Instruct model in 4-bit precision...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Create a pipeline for the model
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.1,
    do_sample=True
)

# Create a LangChain wrapper for the model
llm = HuggingFacePipeline(
    pipeline=pipe,
    model_kwargs={{"temperature": 0.7}}
)

# Define tools for the dental agent
def get_clinic_info():
    \"\"\"Get information about Romi Dental Clinic\"\"\"
    return {
        "name": "Romi Dental Clinic",
        "location": "Albania",
        "services": [
            "Regular check-ups and cleanings",
            "Cosmetic dentistry and whitening",
            "Emergency dental care",
            "Children's dentistry",
            "Dental implants and prosthetics"
        ],
        "payment_methods": ["Cash", "Credit cards", "Bank transfers"],
        "special_offers": "Free initial consultation for new patients"
    }

def check_available_slots():
    \"\"\"Check available appointment slots at the clinic\"\"\"
    # This would normally connect to a real booking system
    # For demo purposes, we'll return some fake slots
    today = datetime.datetime.now()
    available_slots = []
    
    for i in range(1, 6):  # Next 5 days
        day = today + datetime.timedelta(days=i)
        if day.weekday() < 5:  # Weekdays
            available_slots.append({
                "date": day.strftime("%Y-%m-%d"),
                "slots": ["09:00", "11:30", "14:00", "16:30"]
            })
        elif day.weekday() == 5:  # Saturday
            available_slots.append({
                "date": day.strftime("%Y-%m-%d"),
                "slots": ["09:00", "11:30"]
            })
    
    return available_slots

def schedule_appointment(date, time, name, phone, service):
    \"\"\"Schedule a dental appointment\"\"\"
    # This would normally connect to a real booking system
    # For demo purposes, we'll just return a confirmation message
    return f"Appointment scheduled for {{name}} on {{date}} at {{time}} for {{service}}. We'll send a confirmation to {{phone}}."

# Define the tools
tools = [
    Tool(
        name="GetClinicInfo",
        func=get_clinic_info,
        description="Get information about Romi Dental Clinic, including services, location, and payment methods."
    ),
    Tool(
        name="CheckAvailableSlots",
        func=check_available_slots,
        description="Check available appointment slots at the clinic for the next few days."
    ),
    Tool(
        name="ScheduleAppointment",
        func=schedule_appointment,
        description="Schedule a dental appointment. Requires date, time, name, phone number, and service."
    )
]

# Create a memory for the conversation
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create the agent
agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=PromptTemplate.from_template(AGENT_INSTRUCTION),
    verbose=True
)

# Create the agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

# Interactive mode
if __name__ == "__main__":
    print("=" * 50)
    print("ROMI DENTAL CLINIC OUTBOUND CALLING AGENT")
    print("=" * 50)
    print("Agent loaded! Enter client responses (type 'exit' to quit)")
    print("=" * 50)
    
    # Start with the opening message
    print("\\nElo: Good morning! I'm Elo from Romi Dental Clinic. I'm reaching out to understand how we can help with your dental health. How long has it been since your last check-up?")
    
    while True:
        user_input = input("\\nClient: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        print("\\nElo is thinking...")
        response = agent_executor.run(input=user_input)
        print(f"\\nElo: {{response}}")
"""
    
    with open(script_path, "w") as f:
        f.write(script_content)
    
    print(f"✅ Created dental outbound agent script at {script_path}")
    return script_path

def main():
    print("=" * 50)
    print("ROMI DENTAL CLINIC OUTBOUND CALLING AGENT SETUP")
    print("=" * 50)
    
    # Setup the Python environment
    setup_environment()
    
    # Check GPU compatibility
    check_gpu_compatibility()
    
    # Authenticate with Hugging Face
    authenticate_huggingface()
    
    # Download Llama 3.1 8B Instruct model
    model_dir = download_llama3_1()
    
    if model_dir:
        # Create dental agent script
        script_path = create_dental_agent_script(model_dir)
        
        print("\n" + "=" * 50)
        print("SETUP COMPLETE!")
        print("=" * 50)
        print(f"Llama 3.1 8B model downloaded to: {model_dir}")
        print(f"To start your dental outbound calling agent, run: python {script_path}")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("SETUP FAILED")
        print("Please check the error messages above and try again.")
        print("=" * 50)

if __name__ == "__main__":
    main()