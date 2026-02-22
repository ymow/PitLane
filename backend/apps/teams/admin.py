from django.contrib import admin
from apps.teams.models import Driver, Team, DriverContract, SocialHandle, TeamSponsor


class DriverContractInline(admin.TabularInline):
    model = DriverContract
    extra = 0
    fields = ('driver', 'person_name', 'role', 'season', 'car_number',
              'is_active', 'valid_from', 'valid_until')
    raw_id_fields = ('driver', 'season')


class SocialHandleInline(admin.TabularInline):
    model = SocialHandle
    extra = 0
    fields = ('platform', 'handle', 'url', 'entity_type', 'is_verified', 'is_active')
    fk_name = 'driver'


class TeamSocialHandleInline(admin.TabularInline):
    model = SocialHandle
    extra = 0
    fields = ('platform', 'handle', 'url', 'entity_type', 'is_verified', 'is_active')
    fk_name = 'team'


class TeamSponsorInline(admin.TabularInline):
    model = TeamSponsor
    extra = 0
    fields = ('sponsor', 'sponsorship_type', 'is_title_sponsor', 'valid_from', 'valid_until')
    raw_id_fields = ('sponsor',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display  = ('code', 'base_name', 'country', 'is_active')
    list_filter   = ('is_active', 'country')
    search_fields = ('code', 'base_name')
    inlines       = [DriverContractInline, TeamSocialHandleInline, TeamSponsorInline]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display  = ('code', 'full_name', 'nationality', 'racing_number', 'status', 'is_active')
    list_filter   = ('status', 'is_active', 'nationality')
    search_fields = ('code', 'first_name', 'last_name', 'full_name')
    inlines       = [DriverContractInline, SocialHandleInline]


@admin.register(DriverContract)
class DriverContractAdmin(admin.ModelAdmin):
    list_display  = ('display_person', 'role', 'team', 'season', 'is_active', 'valid_from')
    list_filter   = ('role', 'is_active', 'team', 'season')
    search_fields = ('driver__full_name', 'person_name', 'team__base_name')
    raw_id_fields = ('driver', 'team', 'season')

    def display_person(self, obj):
        return obj.driver.full_name if obj.driver else obj.person_name
    display_person.short_description = 'Person'


@admin.register(SocialHandle)
class SocialHandleAdmin(admin.ModelAdmin):
    list_display  = ('handle', 'platform', 'entity_type', 'driver', 'team',
                      'staff_name', 'role', 'is_verified', 'is_active', 'follower_count')
    list_filter   = ('platform', 'entity_type', 'is_verified', 'is_active')
    search_fields = ('handle', 'staff_name', 'role', 'driver__last_name', 'team__base_name')
    raw_id_fields = ('driver', 'team')
