from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp_esa.models import EsaCommunity


class EsaCommunityTagInline(admin.TabularInline):
    model = EsaCommunity.tags.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunitySectorInline(admin.TabularInline):
    model = EsaCommunity.sectors.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunitySpaceInline(admin.TabularInline):
    model = EsaCommunity.spaces.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunityInline(admin.StackedInline):
    model = EsaCommunity
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunityAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'community')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    inlines = [EsaCommunityTagInline,
               EsaCommunitySectorInline, EsaCommunitySpaceInline]
    search_fields = ['urlid', 'community', 'name']
    ordering = ['urlid']


admin.site.register(EsaCommunity, EsaCommunityAdmin)
