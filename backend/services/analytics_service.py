from database.db import db
from models.compliance import Compliance
from models.user import User
from datetime import datetime, date, timedelta  # ← Added timedelta
from sqlalchemy import func, extract

class AnalyticsService:
    """Service class for analytics and reporting"""
    
    @staticmethod
    def get_completion_rate():
        """Get overall completion rate"""
        total = Compliance.query.count()
        if total == 0:
            return 0
        completed = Compliance.query.filter_by(status='Completed').count()
        return round((completed / total) * 100, 2)
    
    @staticmethod
    def get_status_distribution():
        """Get distribution of compliance statuses"""
        statuses = ['Completed', 'Ongoing', 'Planned', 'Overdue']
        result = {}
        for status in statuses:
            count = Compliance.query.filter_by(status=status).count()
            result[status] = count
        return result
    
    @staticmethod
    def get_category_distribution():
        """Get distribution of compliance by category"""
        categories = db.session.query(
            Compliance.category,
            func.count(Compliance.id).label('count')
        ).group_by(Compliance.category).all()
        
        return [{'category': c[0], 'count': c[1]} for c in categories]
    
    @staticmethod
    def get_monthly_completion(year=None):
        """Get monthly completion data for a given year"""
        if not year:
            year = date.today().year
        
        monthly_data = []
        for month in range(1, 13):
            count = Compliance.query.filter(
                extract('year', Compliance.completion_date) == year,
                extract('month', Compliance.completion_date) == month,
                Compliance.status == 'Completed'
            ).count()
            monthly_data.append({
                'month': month,
                'count': count
            })
        
        return monthly_data
    
    @staticmethod
    def get_upcoming_deadlines(days=30):
        """Get upcoming deadlines within specified days"""
        today = date.today()
        end_date = today + timedelta(days=days)  # ← Now timedelta is defined
        
        upcoming = Compliance.query.filter(
            Compliance.valid_date >= today,
            Compliance.valid_date <= end_date,
            Compliance.status != 'Completed'
        ).order_by(Compliance.valid_date.asc()).all()
        
        return [c.to_dict() for c in upcoming]
    
    @staticmethod
    def get_overdue_count():
        """Get count of overdue compliance"""
        today = date.today()
        return Compliance.query.filter(
            Compliance.valid_date < today,
            Compliance.status != 'Completed'
        ).count()
    
    @staticmethod
    def get_authority_wise_count():
        """Get count of compliance by authority"""
        authorities = db.session.query(
            Compliance.authority,
            func.count(Compliance.id).label('count')
        ).group_by(Compliance.authority).order_by(
            func.count(Compliance.id).desc()
        ).limit(10).all()
        
        return [{'authority': a[0], 'count': a[1]} for a in authorities]
    
    @staticmethod
    def get_priority_distribution():
        """Get distribution of compliance by priority"""
        priorities = ['High', 'Medium', 'Low']
        result = {}
        for priority in priorities:
            count = Compliance.query.filter_by(priority=priority).count()
            result[priority] = count
        return result
    
    @staticmethod
    def get_summary_stats():
        """Get comprehensive summary statistics"""
        total = Compliance.query.count()
        completed = Compliance.query.filter_by(status='Completed').count()
        ongoing = Compliance.query.filter_by(status='Ongoing').count()
        planned = Compliance.query.filter_by(status='Planned').count()
        overdue = Compliance.query.filter_by(status='Overdue').count()
        
        today = date.today()
        due_this_month = Compliance.query.filter(
            extract('year', Compliance.valid_date) == today.year,
            extract('month', Compliance.valid_date) == today.month,
            Compliance.status != 'Completed'
        ).count()
        
        return {
            'total': total,
            'completed': completed,
            'ongoing': ongoing,
            'planned': planned,
            'overdue': overdue,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'due_this_month': due_this_month
        }

    @staticmethod
    def get_trend_data():
        """Get trend data for last 12 months"""
        today = date.today()
        trend_data = []
        
        for i in range(11, -1, -1):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            
            month_name = datetime(year, month, 1).strftime('%b')
            
            # Count compliance created in this month
            created = Compliance.query.filter(
                extract('year', Compliance.created_at) == year,
                extract('month', Compliance.created_at) == month
            ).count()
            
            # Count compliance completed in this month
            completed = Compliance.query.filter(
                extract('year', Compliance.completion_date) == year,
                extract('month', Compliance.completion_date) == month,
                Compliance.status == 'Completed'
            ).count()
            
            trend_data.append({
                'month': month_name,
                'created': created,
                'completed': completed
            })
        
        return trend_data