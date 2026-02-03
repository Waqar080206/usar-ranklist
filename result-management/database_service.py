# database_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from models import Student, SemesterResult, Branch, StudentSummary, BranchStats, SemesterStats
import os

class DatabaseService:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        self.db = self.client.results_management
        self.students = self.db.students
        
    async def setup_indexes(self):
        """Create indexes for efficient querying"""
        await self.students.create_index("roll_number", unique=True)
        await self.students.create_index("registration_number", unique=True)
        await self.students.create_index("branch")
        await self.students.create_index("current_semester")
        await self.students.create_index("batch_year")
        await self.students.create_index([("branch", 1), ("current_semester", 1)])
        await self.students.create_index([("branch", 1), ("cgpa", -1)])
        await self.students.create_index("semester_results.semester")
        
    # ============ CRUD Operations ============
    
    async def create_student(self, student: Student) -> str:
        """Insert a new student"""
        result = await self.students.insert_one(student.dict())
        return str(result.inserted_id)
    
    async def get_student(self, roll_number: str) -> Optional[Student]:
        """Get student by roll number"""
        doc = await self.students.find_one({"roll_number": roll_number})
        return Student(**doc) if doc else None
    
    async def update_student(self, roll_number: str, update_data: dict) -> bool:
        """Update student data"""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.students.update_one(
            {"roll_number": roll_number},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def add_semester_result(self, roll_number: str, result: SemesterResult) -> bool:
        """Add or update semester result for a student"""
        # Remove existing result for this semester if any
        await self.students.update_one(
            {"roll_number": roll_number},
            {"$pull": {"semester_results": {"semester": result.semester}}}
        )
        # Add new result
        update_result = await self.students.update_one(
            {"roll_number": roll_number},
            {
                "$push": {"semester_results": result.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        # Recalculate CGPA
        await self._update_cgpa(roll_number)
        return update_result.modified_count > 0
    
    async def _update_cgpa(self, roll_number: str):
        """Recalculate and update CGPA"""
        student = await self.get_student(roll_number)
        if student and student.semester_results:
            total_credits = sum(r.credits_earned for r in student.semester_results)
            weighted_sum = sum(
                r.sgpa * r.credits_earned for r in student.semester_results
            )
            cgpa = weighted_sum / total_credits if total_credits > 0 else 0
            await self.students.update_one(
                {"roll_number": roll_number},
                {"$set": {"cgpa": round(cgpa, 2)}}
            )
    
    # ============ Query Operations ============
    
    async def get_students_by_branch(
        self, 
        branch: Branch,
        semester: Optional[int] = None,
        batch_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "roll_number",
        sort_order: int = 1
    ) -> List[Student]:
        """Get students filtered by branch and optionally semester"""
        query = {"branch": branch.value}
        if semester:
            query["current_semester"] = semester
        if batch_year:
            query["batch_year"] = batch_year
            
        cursor = self.students.find(query)\
            .sort(sort_by, sort_order)\
            .skip(skip)\
            .limit(limit)
        
        return [Student(**doc) async for doc in cursor]
    
    async def get_students_by_semester(
        self,
        semester: int,
        branch: Optional[Branch] = None,
        batch_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Student]:
        """Get students filtered by semester"""
        query = {"current_semester": semester}
        if branch:
            query["branch"] = branch.value
        if batch_year:
            query["batch_year"] = batch_year
            
        cursor = self.students.find(query)\
            .sort("roll_number", 1)\
            .skip(skip)\
            .limit(limit)
        
        return [Student(**doc) async for doc in cursor]
    
    async def get_semester_results(
        self,
        semester: int,
        branch: Branch,
        batch_year: Optional[int] = None,
        sort_by_sgpa: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all results for a specific semester and branch"""
        pipeline = [
            {"$match": {"branch": branch.value}},
            {"$unwind": "$semester_results"},
            {"$match": {"semester_results.semester": semester}},
        ]
        
        if batch_year:
            pipeline[0]["$match"]["batch_year"] = batch_year
        
        pipeline.extend([
            {"$project": {
                "roll_number": 1,
                "name": 1,
                "branch": 1,
                "batch_year": 1,
                "semester_result": "$semester_results"
            }},
            {"$sort": {"semester_result.sgpa": -1 if sort_by_sgpa else 1}}
        ])
        
        cursor = self.students.aggregate(pipeline)
        return [doc async for doc in cursor]
    
    async def get_branch_toppers(
        self,
        branch: Branch,
        semester: Optional[int] = None,
        limit: int = 10
    ) -> List[StudentSummary]:
        """Get top students in a branch"""
        query = {"branch": branch.value}
        if semester:
            query["current_semester"] = semester
            
        cursor = self.students.find(query)\
            .sort("cgpa", -1)\
            .limit(limit)
        
        return [
            StudentSummary(
                roll_number=doc["roll_number"],
                name=doc["name"],
                branch=doc["branch"],
                current_semester=doc["current_semester"],
                cgpa=doc["cgpa"],
                overall_status=doc["overall_status"]
            )
            async for doc in cursor
        ]
    
    async def get_branch_statistics(
        self,
        branch: Branch,
        semester: Optional[int] = None
    ) -> BranchStats:
        """Get statistics for a branch"""
        match_stage = {"branch": branch.value}
        if semester:
            match_stage["current_semester"] = semester
            
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": "$branch",
                "total_students": {"$sum": 1},
                "pass_count": {
                    "$sum": {"$cond": [{"$eq": ["$overall_status", "ACTIVE"]}, 1, 0]}
                },
                "fail_count": {
                    "$sum": {"$cond": [{"$eq": ["$overall_status", "DETAINED"]}, 1, 0]}
                },
                "avg_cgpa": {"$avg": "$cgpa"}
            }}
        ]
        
        cursor = self.students.aggregate(pipeline)
        stats = await cursor.to_list(1)
        
        if stats:
            stat = stats[0]
            toppers = await self.get_branch_toppers(branch, semester, 5)
            return BranchStats(
                branch=branch.value,
                total_students=stat["total_students"],
                pass_count=stat["pass_count"],
                fail_count=stat["fail_count"],
                pass_percentage=round(stat["pass_count"] / stat["total_students"] * 100, 2),
                average_sgpa=round(stat["avg_cgpa"], 2),
                toppers=toppers
            )
        return None
    
    async def search_students(
        self,
        query: str,
        branch: Optional[Branch] = None,
        semester: Optional[int] = None
    ) -> List[StudentSummary]:
        """Search students by name or roll number"""
        search_query = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"roll_number": {"$regex": query, "$options": "i"}}
            ]
        }
        if branch:
            search_query["branch"] = branch.value
        if semester:
            search_query["current_semester"] = semester
            
        cursor = self.students.find(search_query).limit(20)
        
        return [
            StudentSummary(
                roll_number=doc["roll_number"],
                name=doc["name"],
                branch=doc["branch"],
                current_semester=doc["current_semester"],
                cgpa=doc["cgpa"],
                overall_status=doc["overall_status"]
            )
            async for doc in cursor
        ]
    
    async def get_all_semesters_summary(self, branch: Branch) -> List[Dict]:
        """Get summary of all semesters for a branch"""
        pipeline = [
            {"$match": {"branch": branch.value}},
            {"$unwind": "$semester_results"},
            {"$group": {
                "_id": "$semester_results.semester",
                "student_count": {"$sum": 1},
                "avg_sgpa": {"$avg": "$semester_results.sgpa"},
                "pass_count": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$semester_results.result_status", "PASS"]}, 
                            1, 
                            0
                        ]
                    }
                }
            }},
            {"$sort": {"_id": 1}}
        ]
        
        cursor = self.students.aggregate(pipeline)
        return [doc async for doc in cursor]

# Singleton instance
db_service = DatabaseService()