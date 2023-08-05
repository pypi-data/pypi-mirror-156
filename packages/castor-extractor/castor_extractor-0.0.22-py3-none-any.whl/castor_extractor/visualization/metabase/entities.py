from enum import Enum


class MetabaseEntity(Enum):
    """
    Entities that can be fetched from Metabase
    """

    COLLECTION = "collection"
    USER = "user"
    DATABASE = "database"
    TABLE = "table"
    CARD = "card"
    DASHBOARD = "dashboard"
    DASHBOARD_CARDS = "dashboard_cards"


EXPORTED_FIELDS = {
    MetabaseEntity.COLLECTION: (
        "id",
        "name",
        "description",
        "color",
        "archived",
        "location",
        "personal_owner_id",
        "slug",
        "namespace",
    ),
    MetabaseEntity.USER: (
        "id",
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "last_login",
        "is_superuser",
        "is_active",
        "updated_at",
        "locale",
    ),
    MetabaseEntity.DATABASE: (
        "id",
        "created_at",
        "updated_at",
        "name",
        "description",
        "engine",
        "is_sample",
        "is_full_sync",
        "points_of_interest",
        "caveats",
        "metadata_sync_schedule",
        "cache_field_values_schedule",
        "timezone",
        "is_on_demand",
        "options",
        "auto_run_queries",
        "dbname",  # calculated field
    ),
    MetabaseEntity.TABLE: (
        "id",
        "created_at",
        "updated_at",
        "name",
        "description",
        "entity_name",
        "entity_type",
        "active",
        "db_id",
        "display_name",
        "visibility_type",
        "schema",
        "points_of_interest",
        "caveats",
        "show_in_getting_started",
        "field_order",
    ),
    MetabaseEntity.CARD: (
        "id",
        "created_at",
        "updated_at",
        "name",
        "description",
        "display",
        "dataset_query",
        "visualization_settings",
        "creator_id",
        "database_id",
        "table_id",
        "query_type",
        "archived",
        "collection_id",
        "made_public_by_id",
        "enable_embedding",
        "embedding_params",
        "result_metadata",
        "collection_position",
        "view_count",
    ),
    MetabaseEntity.DASHBOARD: (
        "id",
        "created_at",
        "updated_at",
        "name",
        "description",
        "creator_id",
        "parameters",
        "points_of_interest",
        "caveats",
        "show_in_getting_started",
        "made_public_by_id",
        "enable_embedding",
        "embedding_params",
        "archived",
        "position",
        "collection_id",
        "collection_position",
        "view_count",
    ),
    MetabaseEntity.DASHBOARD_CARDS: (
        "id",
        "card_id",
        "dashboard_id",
        "created_at",
        "updated_at",
        "sizex",
        "sizey",
        "row",
        "col",
        "parameter_mappings",
        "visualization_settings",
    ),
}
