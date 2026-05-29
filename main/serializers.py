from datetime import timedelta, datetime
from rest_framework import serializers
from django.db import models
from .models import HomePage, Event, Service, Tariff, Application, Program, Assignment, Staff, StaffGroup

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'
        
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    show_name = serializers.ReadOnlyField(source='chosen_show.title')
    program_name = serializers.ReadOnlyField(source='chosen_program.title')
    tariff = serializers.StringRelatedField()
    chosen_show = serializers.StringRelatedField()
    chosen_program = serializers.StringRelatedField()
    assigned_target = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'category', 'full_name', 'phone', 'email', 
            'age', 'address', 'event_date', 'event_time', 
            'tariff', 'tariff_name', 
            'chosen_show', 'show_name',
            'chosen_program', 'program_name',
            'guests_count', 'message', 'status', 'created_at',
            'assigned_target'
        ]
    
    def get_assigned_target(self, obj):
        assign = Assignment.objects.filter(application=obj).first()
        if assign:
            if assign.group:
                return {'type': 'group', 'id': assign.group.id, 'name': assign.group.name}
            if assign.staff:
                return {'type': 'staff', 'id': assign.staff.id, 'name': assign.staff.full_name}
        return None

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class StaffWithConflictSerializer(serializers.ModelSerializer):
    is_busy = serializers.SerializerMethodField()
    busy_with = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'roles', 'is_busy', 'busy_with']

    def get_is_busy(self, obj):
        target_obj = self.context.get('target_event_obj')
        if not target_obj: return False
            
        curr_start, curr_end = Assignment.calculate_intervals(target_obj)
        if not curr_start: return False

        current_assignment_id = self.context.get('current_assignment_id')
        others = Assignment.objects.filter(
            models.Q(staff_id=obj.id) | models.Q(group__members__id=obj.id)
        )
        if current_assignment_id:
            others = others.exclude(pk=current_assignment_id)

        target_date = getattr(target_obj, 'event_date', getattr(target_obj, 'date', None))
        if hasattr(target_date, 'date'): target_date = target_date.date()

        for other in others.distinct():
            other_obj = other.application if other.application else other.event
            if not other_obj: continue
            
            other_date = getattr(other_obj, 'event_date', getattr(other_obj, 'date', None))
            if hasattr(other_date, 'date'): other_date = other_date.date()
            
            if target_date != other_date: continue

            o_start, o_end = Assignment.calculate_intervals(other_obj)
            if o_start and o_end and (curr_start < o_end and curr_end > o_start):
                return True
        return False

    def get_busy_with(self, obj):
        target_obj = self.context.get('target_event_obj')
        if not target_obj: return None
        curr_start, curr_end = Assignment.calculate_intervals(target_obj)
        if not curr_start: return None

        current_assignment_id = self.context.get('current_assignment_id')
        others = Assignment.objects.filter(
            models.Q(staff_id=obj.id) | models.Q(group__members__id=obj.id)
        )
        if current_assignment_id:
            others = others.exclude(pk=current_assignment_id)

        target_date = getattr(target_obj, 'event_date', getattr(target_obj, 'date', None))
        if hasattr(target_date, 'date'): target_date = target_date.date()

        for other in others.distinct():
            other_obj = other.application if other.application else other.event
            if not other_obj: continue
            
            other_date = getattr(other_obj, 'event_date', getattr(other_obj, 'date', None))
            if hasattr(other_date, 'date'): other_date = other_date.date()
            
            if target_date != other_date: continue

            o_start, o_end = Assignment.calculate_intervals(other_obj)
            if o_start and o_end and (curr_start < o_end and curr_end > o_start):
                return {
                    'title': str(other_obj),
                    'time': f"{o_start.strftime('%H:%M')}-{o_end.strftime('%H:%M')}"
                }
        return None

class StaffGroupSerializer(serializers.ModelSerializer):
    members = StaffWithConflictSerializer(many=True, read_only=True)
    has_busy_members = serializers.SerializerMethodField()
    member_names = serializers.StringRelatedField(source='members', many=True, read_only=True)

    class Meta:
        model = StaffGroup
        fields = ['id', 'name', 'members', 'member_names', 'has_busy_members']

    def get_has_busy_members(self, obj):
        target_obj = self.context.get('target_event_obj')
        if not target_obj: return False
            
        serializer = StaffWithConflictSerializer(
            obj.members.all(), 
            many=True, 
            context=self.context
        )
        return any(member['is_busy'] for member in serializer.data)

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        if 'members' in data:
            internal_data['members'] = data['members']
        return internal_data

    def create(self, validated_data):
        members = validated_data.pop('members', None)
        instance = StaffGroup.objects.create(**validated_data)
        if members is not None:
            instance.members.set(members)
        return instance

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'staff', 'group', 'application', 'event']

    def validate(self, data):
        staff = data.get('staff') or (self.instance.staff if self.instance else None)
        group = data.get('group') or (self.instance.group if self.instance else None)
        app = data.get('application') or (self.instance.application if self.instance else None)
        event = data.get('event') or (self.instance.event if self.instance else None)

        target_obj = app if app else event
        if not target_obj:
            raise serializers.ValidationError("Необходимо выбрать мероприятие.")
        if not staff and not group:
            raise serializers.ValidationError("Необходимо выбрать сотрудника или команду.")

        target_date = getattr(target_obj, 'event_date', getattr(target_obj, 'date', None))
        if hasattr(target_date, 'date'): target_date = target_date.date()
        
        curr_start, curr_end = Assignment.calculate_intervals(target_obj)
        if curr_start:
            staff_list = [staff] if staff else list(group.members.all())
            
            for person in staff_list:
                existing = Assignment.objects.filter(
                    models.Q(staff=person) | models.Q(group__members=person)
                ).distinct()
                if self.instance:
                    existing = existing.exclude(pk=self.instance.pk)

                for other in existing:
                    other_obj = other.application if other.application else other.event
                    if not other_obj: continue
                    
                    other_date = getattr(other_obj, 'event_date', getattr(other_obj, 'date', None))
                    if hasattr(other_date, 'date'): other_date = other_date.date()
                    
                    if target_date != other_date: continue

                    o_start, o_end = Assignment.calculate_intervals(other_obj)
                    if o_start and o_end and (curr_start < o_end and curr_end > o_start):
                        raise serializers.ValidationError(
                            f"Сотрудник {person.full_name} занят на событии '{other_obj}' ({o_start.strftime('%H:%M')}-{o_end.strftime('%H:%M')})."
                        )
        return data