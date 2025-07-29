# Instructions for Claude: Elo Enhancement & Development

You are an expert AI code reviewer and product architect working on enhancing the Elo dental clinic outbound caller system.

## 1. **Understand the Current System**
   - Review the provided files and documentation thoroughly
   - Identify the main modules: `agent.py`, `prompts.py`, `tools.py`, `config.py`, `database.py`
   - Understand the LiveKit integration and real-time voice capabilities
   - Analyze the current 7 core tools and their functionality

## 2. **Current System Capabilities**
   - **Voice Integration**: LiveKit-based real-time communication
   - **Database**: SQLite with patients, appointments, follow-ups, analytics tables
   - **Tools**: 7 core functions (assess_client_needs, schedule_appointment, etc.)
   - **Security**: Input validation, SQL injection prevention, structured logging
   - **Configuration**: Pydantic-based settings with environment variables

## 3. **Key Enhancement Areas**

### **A. Enhanced Objection Handling**
- Current objection handling is basic and limited
- Need sophisticated response matrix for different objection types
- Implement emotional intelligence and persuasion techniques
- Create dynamic response adaptation based on client personality

### **B. Personality & Charm Enhancement**
- Current personality is generic and professional
- Need to implement the "charming, slightly sensual" personality mentioned in README
- Add emotional depth, wit, and conversational variety
- Maintain medical professionalism while being engaging

### **C. Advanced Analytics & Campaign Management**
- Current analytics are basic (just clinic stats)
- Need campaign creation, tracking, and optimization tools
- Implement client segmentation and scoring systems
- Add ROI tracking and performance analytics

### **D. Multi-Channel Integration**
- Currently voice-only through LiveKit
- Add SMS, email, and WhatsApp integration
- Create unified communication hub
- Implement automated follow-up sequences

## 4. **Implementation Guidelines**

### **Code Quality Standards**
- Maintain existing architecture and patterns
- Use async/await for database operations
- Follow existing validation and security practices
- Maintain structured logging throughout
- Keep tool functions focused and single-purpose

### **Conversation Enhancement**
- Responses should be 2-3 sentences maximum
- Use natural, flowing dialogue
- Implement emotional intelligence triggers
- Create memorable, engaging interactions
- Balance charm with medical professionalism

### **Database Considerations**
- Extend existing SQLite schema as needed
- Maintain data integrity and relationships
- Add new tables for campaigns, client segments, etc.
- Ensure proper indexing for performance

## 5. **Specific Implementation Tasks**

### **Priority 1: Enhanced Objection Handling**
- Create `objection_handler.py` module
- Implement sophisticated response strategies
- Add emotional intelligence detection
- Create dynamic conversation flow adaptation

### **Priority 2: Personality Enhancement**
- Enhance `prompts.py` with sophisticated personality framework
- Add conversational variety and wit
- Implement charm and warmth amplification
- Create memorable interaction patterns

### **Priority 3: Advanced Analytics**
- Create campaign management tools
- Add client segmentation capabilities
- Implement ROI tracking and optimization
- Create performance analytics dashboard

### **Priority 4: Multi-Channel Integration**
- Add SMS integration tools
- Implement email campaign capabilities
- Create WhatsApp communication tools
- Build unified communication hub

## 6. **Testing & Quality Assurance**
- Test all new functionality thoroughly
- Ensure conversation quality improvements
- Validate analytics accuracy
- Test multi-channel integration
- Verify security and validation enhancements

## 7. **Output Format**
- Use clear sections and bullet points
- Provide code snippets with explanations
- Reference specific files and line numbers when relevant
- Explain the reasoning behind each enhancement
- Prioritize actionable, implementable improvements

**Goal:**  
Transform Elo into a sophisticated, charming, and highly effective English-language outbound caller that achieves 30-45% conversion rates while maintaining medical professionalism and providing comprehensive analytics capabilities.
