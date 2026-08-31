# MCP 도구 전체 목록

- 서버: https://mcp.facebook.com/ads
- 실측 수집: 2026-07-29 / 총 **97개**
- 인자 스펙 확인: `python3 ../scripts/mcp.py schema <도구명>`

## ⭐생성·수정·라이브 (7)

| 도구 | 설명 |
|---|---|
| `ads_activate_entity` | Activates a campaign, ad set, or ad by changing its status from PAUSED to ACTIVE, effectively publishing the e |
| `ads_boost_ig_post` | Creates an Instagram ad from an existing IG post. Supports a plan/confirm two-step flow. Only 3 fields are req |
| `ads_create_ad` | Creates a single ad under an existing ad set in PAUSED state. |
| `ads_create_ad_set` | Creates a single ad set under an existing campaign in PAUSED state. BEFORE CALLING: The `ads_create_campaign`  |
| `ads_create_campaign` | Creates a single campaign (campaign group) in PAUSED state. Use this to create just a campaign without an ad s |
| `ads_create_creative` | Creates an ad creative on the specified ad account. Supports four formats: single-image, single-video, Advanta |
| `ads_update_entity` | Updates fields on an existing campaign, ad set, or ad. ## When to use: - Call this tool when the user wants to |

## 리포팅·인사이트 (7)

| 도구 | 설명 |
|---|---|
| `ads_get_ad_entities` | WHEN TO USE: - Use this tool to retrieve ad account data, including entities at levels of ad, adset, campaign, |
| `ads_get_field_context` | Returns rich metadata for ads fields (type, description, filterability, sortability, enum values, aliases, met |
| `ads_insights_advertiser_context` | Provides an overview of the advertiser's business context and marketing funnel to determine the most relevant  |
| `ads_insights_anomaly_signal` | Surfaces alerts and warnings about deviations in ad performance, including unusual patterns, spikes or drops.  |
| `ads_insights_auction_ranking_benchmarks` | Highlights which ads have generated stronger results in the auction and identifies factors (bid, ad quality) t |
| `ads_insights_industry_benchmark` | Compares ad set performance against aggregated benchmarks from similar advertisers, optionally filtered by spe |
| `ads_insights_performance_trend` | Analyzes the direction and changes in key ad performance metrics over time, including Cost Per Click (CPC), Co |

## 조회(계정·페이지·미디어) (17)

| 도구 | 설명 |
|---|---|
| `ads_creative_delete` | Delete an existing ad creative by ID. After deletion, the creative can no longer be used for new ads. ## Requi |
| `ads_creative_update` | Update the MAPI-documented writable fields of an existing ad creative by ID. ## Editable fields (provide at le |
| `ads_creative_upload_image` | Upload an image to an advertiser's ad account image library from a publicly accessible URL. The server downloa |
| `ads_creative_upload_video` | Upload a video to an advertiser's ad account video library from a publicly accessible URL. The server download |
| `ads_entity_get_report` | Polls status and fetches results for an async ad_entities report scheduled via ads_entity_schedule_report. Thi |
| `ads_entity_schedule_report` | Async fallback for ads_get_ad_entities. Schedules an asynchronous ad_entities report and returns a report_run_ |
| `ads_get_ad_account_pages` | Retrieves the list of Facebook Page IDs associated with (promoted under) a given ad account. Results are pagin |
| `ads_get_ad_accounts` | Retrieves the list of ad account IDs that the current user has access to. Results are paginated in chunks of 5 |
| `ads_get_ad_images` | List ad images uploaded to an advertiser's ad account. **IMPORTANT — Partial results**: When called without `h |
| `ads_get_ad_preview` | Generate a visual preview of how an ad creative appears on Facebook, Instagram, Messenger, or other placements |
| `ads_get_ad_videos` | List ad videos uploaded to an advertiser's ad account. **IMPORTANT — Partial results**: When called without `v |
| `ads_get_creative_ads` | Get the ads (adgroups) that use a given ad creative. ## When to use: - The user wants to know which ads refere |
| `ads_get_creatives` | List ad creatives in an advertiser's ad account. **IMPORTANT — Partial results**: When called without `creativ |
| `ads_get_ig_accounts` | Retrieves Instagram accounts linked to an ad account that can be used for creating ads. Results are paginated  |
| `ads_get_ig_media` | Fetches advertisable IG media for a given IG account. Returns posts, reels, and stories that can be promoted.  |
| `ads_get_pages_for_business` | Retrieves the list of Facebook Pages owned by a specific business. Results are paginated in chunks of 50 by de |
| `ads_get_user_pages` | Retrieves all Facebook Pages the current user can use for advertising. Returns pages the user has CREATE_ADS p |

## 진단·도움말 (5)

| 도구 | 설명 |
|---|---|
| `ads_account_get_activity_logs` | Fetches activity log entries for an ad account, showing changes made to campaigns, ad sets, ads, and other ad  |
| `ads_get_errors` | Fetches delivery-blocking errors for campaign, ad set or ad. These are hard-stop issues that keep assets inact |
| `ads_get_help_article` | Retrieves help center articles relevant to the user's question about advertising concepts, policies, or how-to |
| `ads_get_opportunity_score` | Fetches the current opportunity score (0-100) and actionable recommendations for an ad account. META RECOMMEND |
| `ads_library_search` | Searches the Meta Ad Library for ads matching specified criteria. Returns publicly available ad data including |

## A/B·리프트 실험 (7)

| 도구 | 설명 |
|---|---|
| `ads_experiment_abtest_create_test` | Create an A/B test (split test). Supports campaign-level (L3), ad-set-level (L2), and creative-level (L1) test |
| `ads_experiment_abtest_get_test` | Returns details of a specific A/B test by its study ID—name, status, type, start/end dates, and the cells with |
| `ads_experiment_abtest_update_test` | Edits or cancels a running A/B test by study ID. Only the study ID and action are required—the ad account is r |
| `ads_experiment_check_eligibility` | **CRITICAL TRIGGER:** Call this tool whenever a user asks about measuring incrementality, incremental conversi |
| `ads_experiment_lift_create_test` | **CRITICAL TRIGGER:** Act as an advocate for incrementality. Proactively pitch this tool whenever a user evalu |
| `ads_experiment_lift_get_test` | Fetches a single lift study by its study ID and returns full details — cells, objectives, and incremental resu |
| `ads_experiment_list_tests` | Finds A/B tests (also referred to as split tests) and lift studies associated with an ad entity (ad account, c |

## 커스텀 오디언스 (7)

| 도구 | 설명 |
|---|---|
| `ads_create_custom_audience` | Creates a new custom audience under the specified ad account. Supports five audience subtypes: CUSTOM (custome |
| `ads_delete_custom_audience` | Permanently deletes a custom audience by its ID. ## When to use: - Call this tool when the user explicitly ask |
| `ads_get_ad_account_custom_audiences` | Lists custom audiences for a given ad account, with optional filtering by subtype. Results are paginated. ## W |
| `ads_get_custom_audience` | Retrieves details of a specific custom audience by its ID, including size, status, delivery info, and type. ## |
| `ads_get_custom_audience_adsets` | Returns ad sets (adgroups) that use a given custom audience in their targeting. ## When to use: - Call this to |
| `ads_update_custom_audience` | Updates an existing custom audience's metadata by its ID. Supports DFCA (customer list) and WCA (website) audi |
| `ads_update_custom_audience_users` | Adds or removes users in a Data File Custom Audience (DFCA / customer list) by uploading hashed PII rows. Back |

## 픽셀·데이터셋 (13)

| 도구 | 설명 |
|---|---|
| `ads_get_customconversions` | Retrieves a paginated list of custom conversions for an ad account, optionally filtered to a specific dataset  |
| `ads_get_dataset_details` | Retrieves identity and configuration metadata for a dataset (also known as pixel or application), including na |
| `ads_get_dataset_quality` | Retrieves signal quality and health metrics for a dataset (also known as pixel or application), including Even |
| `ads_get_dataset_stats` | Retrieves event volume statistics for a dataset (also known as pixel or application), aggregated over a config |
| `ads_get_datasets` | Retrieves a paginated list of datasets (also known as pixels or applications) owned or assigned to a business  |
| `ads_pixel_event_create` | Creates Meta Pixel conversion event rules. Batch-capable. AUTH: requires either the `ads_management` or `busin |
| `ads_pixel_event_delete` | Deletes Meta Pixel conversion event rules. Batch-capable. Mirrors the same delete semantics the Events Manager |
| `ads_pixel_event_read` | Reads Meta Pixel conversion event rules. Batch-capable. AUTH: requires the `ads_read`, `ads_management`, or `b |
| `ads_pixel_event_update` | Updates Meta Pixel conversion event rules. Currently status-only. Batch-capable. AUTH: requires either the `ad |
| `ads_pixel_parameter_create` | Creates Meta Pixel parameter extractors (CSS or CONSTANT_VALUE), linked to an existing event rule. Batch-capab |
| `ads_pixel_parameter_delete` | Soft-deletes Meta Pixel parameter extractors. Batch-capable. Mirrors the same delete semantics the Events Mana |
| `ads_pixel_parameter_read` | Reads Meta Pixel parameter extractors. Batch-capable. AUTH: requires the `ads_read`, `ads_management`, or `bus |
| `ads_pixel_parameter_update` | Patches Meta Pixel parameter extractors. Batch-capable. AUTH: requires either the `ads_management` or `busines |

## 카탈로그 (34)

| 도구 | 설명 |
|---|---|
| `ads_catalog_create` | Creates a new product catalog for a business and uploads product data in one step, using a feed URL, inline ba |
| `ads_catalog_create_feed_rule` | Create a new transformation rule on a product feed. Feed rules map or transform attributes during ingestion to |
| `ads_catalog_create_product_feed` | Create a new product feed (a "data source") under a catalog. A product feed is the entry point for ingesting p |
| `ads_catalog_create_product_feed_upload_session` | Triggers a new upload session on an existing product feed, forcing an immediate refresh from the configured re |
| `ads_catalog_create_product_set` | Creates a dynamic product set in a catalog from a structured filter rule (see **Filter spec** below) and retur |
| `ads_catalog_delete_product` | Delete a product item from a catalog. The item is removed from the catalog and immediately stops appearing in  |
| `ads_catalog_event_source_connect` | Connect an event source to a product catalog so its signals can be matched against the catalog's products (for |
| `ads_catalog_event_source_disconnect` | Disconnect an event source from a product catalog, removing the link so the source's signals are no longer mat |
| `ads_catalog_event_source_get` | List the event sources connected to a product catalog. Event sources are also commonly called "pixels"; this t |
| `ads_catalog_event_source_get_catalogs` | Get the product catalogs connected to a given event source (pixel, CAPI app, or offline conversion data set).  |
| `ads_catalog_event_source_get_health` | Report the match rate and setup issues for the event sources connected to a product catalog. "Match rate" is t |
| `ads_catalog_event_source_get_recommendations` | Recommend the event sources (pixels) to connect to a product catalog. Meta computes, for catalogs with weak or |
| `ads_catalog_get_catalogs` | Gets the catalogs associated with the authenticated user (up to 100). ## When to use: - Call this tool when th |
| `ads_catalog_get_data_sources` | List ALL data sources connected to a catalog — not just product feeds, but also Batch API, Graph API, partner  |
| `ads_catalog_get_details` | Get catalog details including name, vertical, product/product set counts, business info, and optionally a pagi |
| `ads_catalog_get_diagnostics` | Fetches diagnostic issues for a product catalog, including errors and warnings that may affect ad delivery. ## |
| `ads_catalog_get_dynamic_ads_health` | Run Dynamic Ads (DA) integration health checks for either a product catalog OR a single product set. Each chec |
| `ads_catalog_get_feed_rules` | Gets the data transformation rules applied to a product data feed during ingestion, with cursor-based paginati |
| `ads_catalog_get_product_details` | Fetches a product item from the catalog by its Meta-assigned product item ID (FBID). ## Identifier types — rea |
| `ads_catalog_get_product_feed_details` | Fetches details about a product feed, including its name, schedule configuration, product count, and upload se |
| `ads_catalog_get_product_feed_upload_sessions` | List recent upload sessions for a product feed, most recent first. Each session reports its outcome (status),  |
| `ads_catalog_get_product_product_sets` | List the product sets that contain a given product item, with cursor-based pagination. Useful for understandin |
| `ads_catalog_get_product_set_details` | Fetch details for a single product set by its ID, including name, filter rule, product count, type, visibility |
| `ads_catalog_get_product_set_products` | Gets the products/items in a product set with cursor-based pagination and optional filters. ## When to use: -  |
| `ads_catalog_get_product_sets` | Gets a list of product sets in a catalog with cursor-based pagination. ## When to use: - Call this tool when t |
| `ads_catalog_product_create` | Create a single catalog item. The item's vertical is determined by the target catalog: a commerce/products cat |
| `ads_catalog_product_feed_delete` | Delete a product feed (data source) from a catalog. The feed and its schedule are removed, and the products it |
| `ads_catalog_product_feed_delete_rule` | Permanently delete a transformation rule from a product feed. This action is irreversible — the rule is remove |
| `ads_catalog_product_set_delete` | Permanently delete a product set from a catalog. This action is irreversible — the product set and its filter  |
| `ads_catalog_search_product` | Searches or lists products in a catalog using a structured filter rule (see **Filter spec** below) and returns |
| `ads_catalog_update_catalog` | Update an existing catalog's settings. At least one field besides catalog_id must be provided. When to use: -  |
| `ads_catalog_update_product` | Update one or more fields on an existing product item (catalog product). Only the fields you provide are chang |
| `ads_catalog_update_product_feed` | Update settings on an existing product feed (a "data source") under a catalog. This is the "edit feed" counter |
| `ads_catalog_update_product_set` | Update an existing product set's name, filter rules, visibility, retailer ID, or parent. At least one field be |
