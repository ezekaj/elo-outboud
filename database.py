"""
Database layer for Elo Dental Clinic system
"""
import aiosqlite
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from models import (
    Patient, Appointment, FollowUp, CallAnalytics, 
    AppointmentStatus, FollowUpStatus
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Async database manager for Elo Dental Clinic"""
    
    def __init__(self, db_path: str = "clinic.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def init_db(self):
        """Initialize database with required tables"""
        if self._initialized:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create patients table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create appointments table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    patient_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    scheduled_date TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'scheduled',
                    revenue REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            """)
            
            # Create follow_ups table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS follow_ups (
                    id TEXT PRIMARY KEY,
                    patient_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    preferred_time TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    scheduled_by TEXT DEFAULT 'Elo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Create call_analytics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS call_analytics (
                    id TEXT PRIMARY KEY,
                    total_calls INTEGER DEFAULT 0,
                    appointments_booked INTEGER DEFAULT 0,
                    revenue_generated REAL DEFAULT 0.0,
                    conversion_rate REAL DEFAULT 0.0,
                    date DATE DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(phone_number)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_follow_ups_status ON follow_ups(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone_number)")
            
            await db.commit()
            self._initialized = True
            logger.info("Database initialized successfully")
    
    async def add_patient(self, patient: Patient) -> str:
        """Add a new patient"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO patients (id, name, phone_number, email)
                VALUES (?, ?, ?, ?)
            """, (patient.id, patient.name, patient.phone_number, patient.email))
            await db.commit()
            return patient.id
    
    async def get_patient_by_phone(self, phone_number: str) -> Optional[Patient]:
        """Get patient by phone number"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, phone_number, email, created_at FROM patients WHERE phone_number = ?",
                (phone_number,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Patient(
                        id=row[0],
                        name=row[1],
                        phone_number=row[2],
                        email=row[3],
                        created_at=datetime.fromisoformat(row[4])
                    )
        return None
    
    async def add_appointment(self, appointment: Appointment) -> str:
        """Add a new appointment"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO appointments (
                    id, patient_id, patient_name, phone_number, 
                    service_type, scheduled_date, status, revenue, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                appointment.id,
                appointment.patient_id,
                appointment.patient_name,
                appointment.phone_number,
                appointment.service_type,
                appointment.scheduled_date,
                appointment.status.value,
                appointment.revenue,
                appointment.notes
            ))
            await db.commit()
            
            # Update analytics
            await self._update_analytics(revenue=appointment.revenue)
            return appointment.id
    
    async def get_appointments_by_date(self, date: datetime) -> List[Appointment]:
        """Get appointments for a specific date"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, patient_id, patient_name, phone_number, 
                       service_type, scheduled_date, status, revenue, notes, created_at
                FROM appointments 
                WHERE DATE(scheduled_date) = DATE(?)
                ORDER BY scheduled_date
            """, (date,)) as cursor:
                appointments = []
                async for row in cursor:
                    appointments.append(Appointment(
                        id=row[0],
                        patient_id=row[1],
                        patient_name=row[2],
                        phone_number=row[3],
                        service_type=row[4],
                        scheduled_date=datetime.fromisoformat(row[5]),
                        status=AppointmentStatus(row[6]),
                        revenue=row[7],
                        notes=row[8],
                        created_at=datetime.fromisoformat(row[9])
                    ))
                return appointments
    
    async def add_follow_up(self, follow_up: FollowUp) -> str:
        """Add a new follow-up"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO follow_ups (
                    id, patient_name, phone_number, preferred_time, 
                    reason, status, scheduled_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                follow_up.id,
                follow_up.patient_name,
                follow_up.phone_number,
                follow_up.preferred_time,
                follow_up.reason,
                follow_up.status.value,
                follow_up.scheduled_by
            ))
            await db.commit()
            return follow_up.id
    
    async def get_pending_follow_ups(self) -> List[FollowUp]:
        """Get all pending follow-ups"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, patient_name, phone_number, preferred_time, 
                       reason, status, scheduled_by, created_at
                FROM follow_ups 
                WHERE status = 'pending'
                ORDER BY created_at
            """) as cursor:
                follow_ups = []
                async for row in cursor:
                    follow_ups.append(FollowUp(
                        id=row[0],
                        patient_name=row[1],
                        phone_number=row[2],
                        preferred_time=row[3],
                        reason=row[4],
                        status=FollowUpStatus(row[5]),
                        scheduled_by=row[6],
                        created_at=datetime.fromisoformat(row[7])
                    ))
                return follow_ups
    
    async def update_follow_up_status(self, follow_up_id: str, status: FollowUpStatus):
        """Update follow-up status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE follow_ups 
                SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status.value, datetime.now() if status == FollowUpStatus.COMPLETED else None, follow_up_id))
            await db.commit()
    
    async def get_analytics(self, date: Optional[datetime] = None) -> CallAnalytics:
        """Get analytics for a specific date or today"""
        target_date = date or datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT total_calls, appointments_booked, revenue_generated, conversion_rate
                FROM call_analytics 
                WHERE date = DATE(?)
            """, (target_date,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return CallAnalytics(
                        total_calls=row[0],
                        appointments_booked=row[1],
                        revenue_generated=row[2],
                        conversion_rate=row[3],
                        date=target_date
                    )
        
        # Return empty analytics if none exist
        return CallAnalytics(date=target_date)
    
    async def _update_analytics(self, revenue: float = 0.0):
        """Update daily analytics"""
        today = datetime.now().date()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get current stats
            async with db.execute("""
                SELECT total_calls, appointments_booked, revenue_generated
                FROM call_analytics 
                WHERE date = ?
            """, (today,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    total_calls = row[0] + 1
                    appointments_booked = row[1] + 1
                    revenue_generated = row[2] + revenue
                else:
                    total_calls = 1
                    appointments_booked = 1
                    revenue_generated = revenue
                
                conversion_rate = (appointments_booked / total_calls) * 100 if total_calls > 0 else 0
                
                await db.execute("""
                    INSERT OR REPLACE INTO call_analytics 
                    (id, total_calls, appointments_booked, revenue_generated, conversion_rate, date)
                    VALUES (
                        COALESCE((SELECT id FROM call_analytics WHERE date = ?), ?),
                        ?, ?, ?, ?, ?
                    )
                """, (
                    today, str(uuid.uuid4()),
                    total_calls, appointments_booked, revenue_generated, conversion_rate, today
                ))
                await db.commit()
    
    async def get_clinic_stats(self) -> Dict[str, Any]:
        """Get comprehensive clinic statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total stats
            async with db.execute("""
                SELECT 
                    COUNT(*) as total_appointments,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_appointments,
                    SUM(revenue) as total_revenue,
                    COUNT(DISTINCT phone_number) as unique_patients
                FROM appointments
            """) as cursor:
                total_stats = await cursor.fetchone()
            
            # Today's stats
            today = datetime.now().date()
            async with db.execute("""
                SELECT 
                    COUNT(*) as today_appointments,
                    SUM(revenue) as today_revenue
                FROM appointments
                WHERE DATE(scheduled_date) = ?
            """, (today,)) as cursor:
                today_stats = await cursor.fetchone()
            
            # Pending follow-ups
            async with db.execute("""
                SELECT COUNT(*) as pending_follow_ups
                FROM follow_ups
                WHERE status = 'pending'
            """) as cursor:
                pending_follow_ups = await cursor.fetchone()
            
            return {
                "total_appointments": total_stats[0] or 0,
                "completed_appointments": total_stats[1] or 0,
                "total_revenue": total_stats[2] or 0.0,
                "unique_patients": total_stats[3] or 0,
                "today_appointments": today_stats[0] or 0,
                "today_revenue": today_stats[1] or 0.0,
                "pending_follow_ups": pending_follow_ups[0] or 0
            }


# Global database instance
db_manager = DatabaseManager()
