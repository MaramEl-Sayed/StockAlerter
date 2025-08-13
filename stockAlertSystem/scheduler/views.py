from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .services import get_scheduler
from .serializers import JobSerializer, SchedulerStatusSerializer
import logging

logger = logging.getLogger(__name__)

class SchedulerStatusView(APIView):
    """Get comprehensive scheduler status"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            scheduler = get_scheduler()
            status_info = scheduler.get_scheduler_status()
            serializer = SchedulerStatusSerializer(status_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return Response(
                {"error": "Failed to get scheduler status"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class JobListView(APIView):
    """List all scheduled jobs"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            scheduler = get_scheduler()
            jobs = scheduler.get_jobs()
            serializer = JobSerializer(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return Response(
                {"error": "Failed to list jobs"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StartSchedulerView(APIView):
    """Start the scheduler"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        try:
            scheduler = get_scheduler()
            success = scheduler.start()
            if success:
                return Response(
                    {"message": "Scheduler started successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Failed to start scheduler"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            return Response(
                {"error": "Failed to start scheduler"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StopSchedulerView(APIView):
    """Stop the scheduler"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        try:
            scheduler = get_scheduler()
            success = scheduler.stop()
            if success:
                return Response(
                    {"message": "Scheduler stopped successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Failed to stop scheduler"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            return Response(
                {"error": "Failed to stop scheduler"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RestartSchedulerView(APIView):
    """Restart the scheduler"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        try:
            scheduler = get_scheduler()
            success = scheduler.restart()
            if success:
                return Response(
                    {"message": "Scheduler restarted successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Failed to restart scheduler"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error restarting scheduler: {e}")
            return Response(
                {"error": "Failed to restart scheduler"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PauseJobView(APIView):
    """Pause a specific job"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, job_id):
        try:
            scheduler = get_scheduler()
            success = scheduler.pause_job(job_id)
            if success:
                return Response(
                    {"message": f"Job {job_id} paused successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": f"Failed to pause job {job_id}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return Response(
                {"error": f"Failed to pause job {job_id}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResumeJobView(APIView):
    """Resume a specific job"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, job_id):
        try:
            scheduler = get_scheduler()
            success = scheduler.resume_job(job_id)
            if success:
                return Response(
                    {"message": f"Job {job_id} resumed successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": f"Failed to resume job {job_id}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return Response(
                {"error": f"Failed to resume job {job_id}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RemoveJobView(APIView):
    """Remove a specific job"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, job_id):
        try:
            scheduler = get_scheduler()
            success = scheduler.remove_job(job_id)
            if success:
                return Response(
                    {"message": f"Job {job_id} removed successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": f"Failed to remove job {job_id}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return Response(
                {"error": f"Failed to remove job {job_id}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
