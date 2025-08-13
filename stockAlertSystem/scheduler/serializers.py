from rest_framework import serializers

class JobSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    next_run_time = serializers.DateTimeField(allow_null=True)
    trigger = serializers.CharField()
    active = serializers.BooleanField()

class SchedulerStatusSerializer(serializers.Serializer):
    is_running = serializers.BooleanField()
    job_count = serializers.IntegerField()
    jobs = JobSerializer(many=True)
    next_run_times = serializers.DictField(child=serializers.DateTimeField(allow_null=True))
