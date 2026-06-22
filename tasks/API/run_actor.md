---
title: Run Actor
url: https://docs.apify.com/api/v2/act-runs-post.md
parents:
  - [Apify documentation](https://docs.apify.com/llms.txt)
  - [Apify API documentation](https://docs.apify.com/api.md)
  - [Apify API](https://docs.apify.com/api/v2.md)
  - [Actor runs - Introduction](https://docs.apify.com/api/v2/actors-actor-runs.md)
previous: [Get list of runs](https://docs.apify.com/api/v2/act-runs-get.md)
next: [Run Actor synchronously and return output](https://docs.apify.com/api/v2/act-run-sync-post.md)
---

# Run Actor


```
POST 
https://api.apify.com/v2/actors/:actorId/runs
```


Runs an Actor and immediately returns without waiting for the run to finish.

The POST payload including its `Content-Type` header is passed as `INPUT` to the Actor (usually `application/json`).

The Actor is started with the default options; you can override them using various URL query parameters.

The response is the Run object as returned by the Get run API endpoint.

If you want to wait for the run to finish and receive the actual output of the Actor as the response, please use one of the Run Actor synchronously API endpoints instead.

To fetch the Actor run results that are typically stored in the default dataset, you'll need to pass the ID received in the `defaultDatasetId` field received in the response JSON to the Get dataset items API endpoint.

## Request

### Path Parameters

* **actorId** string required

  Actor ID or a tilde-separated owner's username and Actor name.

  **Example:** `janedoe~my-actor`

### Query Parameters

* **timeout** double

  Optional timeout for the run, in seconds. By default, the run uses the timeout from its configuration.

  **Example:** `60`

  **memory** double

  Memory limit for the run, in megabytes. The amount of memory can be set to a power of 2 with a minimum of 128. By default, the run uses the memory limit from its configuration.

  **Example:** `256`

  **maxItems** double

  Specifies the maximum number of dataset items that will be charged for pay-per-result Actors. This does NOT guarantee that the Actor will return only this many items. It only ensures you won't be charged for more than this number of items. Only works for pay-per-result Actors. Value can be accessed in the actor run using `ACTOR_MAX_PAID_DATASET_ITEMS` environment variable.

  **Example:** `1000`

  **maxTotalChargeUsd** double

  Specifies the maximum cost of the run. This parameter is useful for pay-per-event Actors, as it allows you to limit the amount charged to your subscription. You can access the maximum cost in your Actor by using the `ACTOR_MAX_TOTAL_CHARGE_USD` environment variable.

  **Example:** `5`

  **restartOnError** boolean

  Determines whether the run will be restarted if it fails.

  **Example:** `false`

  **build** string

  Specifies the Actor build to run. It can be either a build tag or build number. By default, the run uses the build from its configuration (typically `latest`).

  **Example:** `0.1.234`

  **waitForFinish** double

  The maximum number of seconds the server waits for the run to finish. By default it is `0`, the maximum value is `60`. <!-- -->If the run finishes in time then the returned run object will have a terminal status (e.g. `SUCCEEDED`), otherwise it will have a transitional status (e.g. `RUNNING`).

  **Example:** `60`

  **webhooks** string

  Specifies optional webhooks associated with the Actor run, which can be used to receive a notification e.g. when the Actor finished or failed. The value is a Base64-encoded JSON array whose items follow the WebhookRepresentation schema. For more information, see [Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).

  **Example:** `dGhpcyBpcyBqdXN0IGV4YW1wbGUK...`

  **forcePermissionLevel** string

  **Possible values:** \[`LIMITED_PERMISSIONS`, `FULL_PERMISSIONS`]

  Overrides the Actor's permission level for this specific run. Use to test restricted permissions before deploying changes to your Actor or to temporarily elevate or restrict access. If you don't specify this parameter, the Actor uses its configured default permission level. For more information on permissions, see the [documentation](https://docs.apify.com/platform/actors/development/permissions).

  **Example:** `LIMITED_PERMISSIONS`

### Bodyrequired

* **object** object

### Status 201

**Response Headers**

* **Location**

**RunUsage**


```json
{
  "data": {
    "id": "HG7ML7M8z78YcAPEB",
    "actId": "HDSasDasz78YcAPEB",
    "userId": "7sT5jcggjjA9fNcxF",
    "actorTaskId": "KJHSKHausidyaJKHs",
    "startedAt": "2019-11-30T07:34:24.202Z",
    "finishedAt": "2019-12-12T09:30:12.202Z",
    "status": "READY",
    "statusMessage": "Actor is running",
    "isStatusMessageTerminal": false,
    "meta": {
      "origin": "DEVELOPMENT",
      "clientIp": "string",
      "userAgent": "string",
      "scheduleId": "string",
      "scheduledAt": "2024-07-29T15:51:28.071Z"
    },
    "pricingInfo": {
      "apifyMarginPercentage": 0,
      "createdAt": "2024-07-29T15:51:28.071Z",
      "startedAt": "2024-07-29T15:51:28.071Z",
      "notifiedAboutFutureChangeAt": "2024-07-29T15:51:28.071Z",
      "notifiedAboutChangeAt": "2024-07-29T15:51:28.071Z",
      "reasonForChange": "string",
      "isPriceChangeNotificationSuppressed": true,
      "forceContainsSignificantPriceChange": true,
      "pricingModel": "PAY_PER_EVENT",
      "pricingPerEvent": {
        "actorChargeEvents": {}
      },
      "minimalMaxTotalChargeUsd": 0
    },
    "stats": {
      "inputBodyLen": 240,
      "migrationCount": 0,
      "rebootCount": 0,
      "restartCount": 0,
      "resurrectCount": 2,
      "memAvgBytes": 267874071.9,
      "memMaxBytes": 404713472,
      "memCurrentBytes": 0,
      "cpuAvgUsage": 33.7532101107538,
      "cpuMaxUsage": 169.650735534941,
      "cpuCurrentUsage": 0,
      "netRxBytes": 103508042,
      "netTxBytes": 4854600,
      "durationMillis": 248472,
      "runTimeSecs": 248.472,
      "metamorph": 0,
      "computeUnits": 0.13804
    },
    "chargedEventCounts": {
      "actor-start": 1,
      "page-crawled": 150,
      "data-extracted": 75
    },
    "options": {
      "build": "latest",
      "timeoutSecs": 300,
      "memoryMbytes": 1024,
      "diskMbytes": 2048,
      "maxItems": 1000,
      "maxTotalChargeUsd": 5
    },
    "buildId": "7sT5jcggjjA9fNcxF",
    "exitCode": 0,
    "generalAccess": "RESTRICTED",
    "defaultKeyValueStoreId": "eJNzqsbPiopwJcgGQ",
    "defaultDatasetId": "wmKPijuyDnPZAPRMk",
    "defaultRequestQueueId": "FL35cSF7jrxr3BY39",
    "storageIds": {
      "datasets": {
        "default": "wmKPijuyDnPZAPRMk"
      },
      "keyValueStores": {
        "default": "eJNzqsbPiopwJcgGQ"
      },
      "requestQueues": {
        "default": "FL35cSF7jrxr3BY39"
      }
    },
    "buildNumber": "0.0.36",
    "containerUrl": "https://g8kd8kbc5ge8.runs.apify.net",
    "isContainerServerReady": true,
    "gitBranchName": "master",
    "usage": {
      "ACTOR_COMPUTE_UNITS": 3,
      "DATASET_READS": 4,
      "DATASET_WRITES": 4,
      "KEY_VALUE_STORE_READS": 5,
      "KEY_VALUE_STORE_WRITES": 3,
      "KEY_VALUE_STORE_LISTS": 5,
      "REQUEST_QUEUE_READS": 2,
      "REQUEST_QUEUE_WRITES": 1,
      "DATA_TRANSFER_INTERNAL_GBYTES": 1,
      "DATA_TRANSFER_EXTERNAL_GBYTES": 3,
      "PROXY_RESIDENTIAL_TRANSFER_GBYTES": 34,
      "PROXY_SERPS": 3
    },
    "usageTotalUsd": 0.2654,
    "usageUsd": {
      "ACTOR_COMPUTE_UNITS": 0.0003,
      "DATASET_READS": 0.0001,
      "DATASET_WRITES": 0.0001,
      "KEY_VALUE_STORE_READS": 0.0001,
      "KEY_VALUE_STORE_WRITES": 0.00005,
      "KEY_VALUE_STORE_LISTS": 0.0001,
      "REQUEST_QUEUE_READS": 0.0001,
      "REQUEST_QUEUE_WRITES": 0.0001,
      "DATA_TRANSFER_INTERNAL_GBYTES": 0.001,
      "DATA_TRANSFER_EXTERNAL_GBYTES": 0.003,
      "PROXY_RESIDENTIAL_TRANSFER_GBYTES": 0.034,
      "PROXY_SERPS": 0.003
    },
    "metamorphs": [
      {
        "createdAt": "2019-11-30T07:39:24.202Z",
        "actorId": "nspoEjklmnsF2oosD",
        "buildId": "ME6oKecqy5kXDS4KQ",
        "inputKey": "INPUT-METAMORPH-1"
      }
    ],
    "platformUsageBillingModel": "USER"
  }
}
```


**Schema**

* **data** object required

  Represents an Actor run and its associated data.

  * **id** string required

    Unique identifier of the Actor run.

    **Example:** `HG7ML7M8z78YcAPEB`

  * **actId** string required

    ID of the Actor that was run.

    **Example:** `HDSasDasz78YcAPEB`

  * **userId** string required

    ID of the user who started the run.

    **Example:** `7sT5jcggjjA9fNcxF`

  * **actorTaskId** string | null nullable

    ID of the Actor task, if the run was started from a task.

    **Example:** `KJHSKHausidyaJKHs`

  * **startedAt** string\<date-time> required

    Time when the Actor run started.

    **Example:** `2019-11-30T07:34:24.202Z`

  * **finishedAt** string,null\<date-time> nullable

    Time when the Actor run finished.

    **Example:** `2019-12-12T09:30:12.202Z`

  * **status** ActorJobStatus (string) required

    Status of an Actor job (run or build).

    **Possible values:** \[`READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `TIMING-OUT`, `TIMED-OUT`, `ABORTING`, `ABORTED`]

  * **statusMessage** string | null nullable

    Detailed message about the run status.

    **Example:** `Actor is running`

  * **isStatusMessageTerminal** boolean | null nullable

    Whether the status message is terminal (final).

    **Example:** `false`

  * **meta** object required

    Metadata about the Actor run.

    * **origin** RunOrigin (string) required

      **Possible values:** \[`DEVELOPMENT`, `WEB`, `API`, `SCHEDULER`, `TEST`, `WEBHOOK`, `ACTOR`, `CLI`, `CI`, `STANDBY`]

    * **clientIp** string | null nullable

      IP address of the client that started the run.

    * **userAgent** string | null nullable

      User agent of the client that started the run.

    * **scheduleId** string | null nullable

      ID of the schedule that triggered the run.

    * **scheduledAt** string,null\<date-time> nullable

      Time when the run was scheduled.

  * **pricingInfo** object

    Pricing information for the Actor.

    * **pricingModel**

      Pricing information for the Actor.

      **Possible values:** \[`PAY_PER_EVENT`, `PRICE_PER_DATASET_ITEM`, `FLAT_PRICE_PER_MONTH`, `FREE`]
      * **PAY\_PER\_EVENT**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **pricingPerEvent** object required

          * **actorChargeEvents** object

            * **property name\*** ActorChargeEvent

              Definition of a single chargeable event for a pay-per-event Actor. Each event is either flat-priced (`eventPriceUsd` is set) or tier-priced (`eventTieredPricingUsd` is set); the two are mutually exclusive.

              * **eventTitle** string required

                Human-readable title shown to users in the billing UI.

              * **eventDescription** string required

                Human-readable description of what triggers this event.

              * **eventPriceUsd** number

                Flat price per event in USD. Present only for non-tiered events. Mutually exclusive with `eventTieredPricingUsd`.

              * **eventTieredPricingUsd** object

                Tiered price-per-event pricing for a single charge event, keyed by subscription tier (e.g. `FREE`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`). The actual price applied is resolved from the user's tier.

                * **property name\*** TieredPricingPerEventEntry

                  A single tier's price-per-event entry.

                  * **tieredEventPriceUsd** number required

                    Price per event in USD for this tier.

              * **isPrimaryEvent** boolean

                Whether this event is the Actor's primary chargeable event.

              * **isOneTimeEvent** boolean

                Whether this event can only be charged once per Actor run.

        * **minimalMaxTotalChargeUsd** number | null nullable

      * **PRICE\_PER\_DATASET\_ITEM**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **unitName** string required

          Name of the unit that is being charged

        * **pricePerUnitUsd** number

          Price per unit in USD. Mutually exclusive with `tieredPricing` - exactly one of the two is present on a pricing record.

        * **tieredPricing** object

          Tiered price-per-dataset-item pricing, keyed by subscription tier (e.g. `FREE`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`). The actual price applied to a run is resolved from the user's tier.

          * **property name\*** TieredPricingPerDatasetItemEntry

            A single tier's price-per-dataset-item entry.

            * **tieredPricePerUnitUsd** number required

              Price per unit in USD for this tier.

      * **FLAT\_PRICE\_PER\_MONTH**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **trialMinutes** integer required

          For how long this Actor can be used for free in trial period

        * **pricePerUnitUsd** number required

          Monthly flat price in USD

      * **FREE**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

  * **stats** object required

    Statistics of the Actor run.

    * **inputBodyLen** integer | null nullable

      **Possible values:** `>= 0`

      **Example:** `240`

    * **migrationCount** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **rebootCount** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **restartCount** integer required

      **Possible values:** `>= 0`

      **Example:** `0`

    * **resurrectCount** integer required

      **Possible values:** `>= 0`

      **Example:** `2`

    * **memAvgBytes** number\
      **Example:** `267874071.9`

    * **memMaxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `404713472`

    * **memCurrentBytes** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **cpuAvgUsage** number\
      **Example:** `33.7532101107538`

    * **cpuMaxUsage** number\
      **Example:** `169.650735534941`

    * **cpuCurrentUsage** number\
      **Example:** `0`

    * **netRxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `103508042`

    * **netTxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `4854600`

    * **durationMillis** integer

      **Possible values:** `>= 0`

      **Example:** `248472`

    * **runTimeSecs** number

      **Possible values:** `>= 0`

      **Example:** `248.472`

    * **metamorph** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **computeUnits** number required

      **Possible values:** `>= 0`

      **Example:** `0.13804`

  * **chargedEventCounts** object

    A map of charged event types to their counts. The keys are event type identifiers defined by the Actor's pricing model (pay-per-event), and the values are the number of times each event was charged during this run.

    * **property name\*** integer

  * **options** object required

    Configuration options for the Actor run.

    * **build** string required\
      **Example:** `latest`

    * **timeoutSecs** integer required

      **Possible values:** `>= 0`

      **Example:** `300`

    * **memoryMbytes** integer required

      **Possible values:** `>= 128` and `<= 32768`

      **Example:** `1024`

    * **diskMbytes** integer required

      **Possible values:** `>= 0`

      **Example:** `2048`

    * **maxItems** integer | null nullable

      **Possible values:** `>= 1`

      **Example:** `1000`

    * **maxTotalChargeUsd** number

      **Possible values:** `>= 0`

      **Example:** `5`

  * **buildId** string required

    ID of the Actor build used for this run.

    **Example:** `7sT5jcggjjA9fNcxF`

  * **exitCode** integer | null nullable

    Exit code of the Actor run process.

    **Example:** `0`

  * **generalAccess** GeneralAccess (string) required

    General access level for the Actor run.

    **Possible values:** \[`ANYONE_WITH_ID_CAN_READ`, `ANYONE_WITH_NAME_CAN_READ`, `FOLLOW_USER_SETTING`, `RESTRICTED`]

    **Example:** `RESTRICTED`

  * **defaultKeyValueStoreId** string required

    ID of the default key-value store for this run.

    **Example:** `eJNzqsbPiopwJcgGQ`

  * **defaultDatasetId** string required

    ID of the default dataset for this run.

    **Example:** `wmKPijuyDnPZAPRMk`

  * **defaultRequestQueueId** string required

    ID of the default request queue for this run.

    **Example:** `FL35cSF7jrxr3BY39`

  * **storageIds** object

    A map of aliased storage IDs associated with this run, grouped by storage type.

    * **datasets** object

      Aliased dataset IDs for this run.

      * **default** string

        ID of the default dataset for this run.

        **Example:** `wmKPijuyDnPZAPRMk`

      * **property name\*** string

    * **keyValueStores** object

      Aliased key-value store IDs for this run.

      * **default** string

        ID of the default key-value store for this run.

        **Example:** `eJNzqsbPiopwJcgGQ`

      * **property name\*** string

    * **requestQueues** object

      Aliased request queue IDs for this run.

      * **default** string

        ID of the default request queue for this run.

        **Example:** `FL35cSF7jrxr3BY39`

      * **property name\*** string

  * **buildNumber** string | null nullable

    Build number of the Actor build used for this run.

    **Possible values:** Value must match regular expression `^([0-9]|[1-9][0-9])\.([0-9]|[1-9][0-9])(\.[1-9][0-9]{0,4})$`

    **Example:** `0.0.36`

  * **containerUrl** string\<uri>

    URL of the container running the Actor.

    **Example:** `https://g8kd8kbc5ge8.runs.apify.net`

  * **isContainerServerReady** boolean | null nullable

    Whether the container's HTTP server is ready to accept requests.

    **Example:** `true`

  * **gitBranchName** string | null nullable

    Name of the git branch used for the Actor build.

    **Example:** `master`

  * **usage** object

    Resource usage statistics for the run.

    * anyOf
      * RunUsage
      * null
      **ACTOR\_COMPUTE\_UNITS** number | null nullable\
      **Example:** `3`
    * **DATASET\_READS** integer | null nullable\
      **Example:** `4`
    * **DATASET\_WRITES** integer | null nullable\
      **Example:** `4`
    * **KEY\_VALUE\_STORE\_READS** integer | null nullable\
      **Example:** `5`
    * **KEY\_VALUE\_STORE\_WRITES** integer | null nullable\
      **Example:** `3`
    * **KEY\_VALUE\_STORE\_LISTS** integer | null nullable\
      **Example:** `5`
    * **REQUEST\_QUEUE\_READS** integer | null nullable\
      **Example:** `2`
    * **REQUEST\_QUEUE\_WRITES** integer | null nullable\
      **Example:** `1`
    * **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
      **Example:** `1`
    * **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
      **Example:** `3`
    * **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
      **Example:** `34`
    * **PROXY\_SERPS** integer | null nullable\
      **Example:** `3`

  * **usageTotalUsd** number | null nullable

    Total cost in USD for this run. Represents what you actually pay. For run owners: includes platform usage (compute units) and/or event costs depending on the Actor's pricing model. For run non-owners: only available for Pay-Per-Event Actors (event costs only). Requires authentication token to access.

    **Example:** `0.2654`

  * **usageUsd** object

    Platform usage costs breakdown in USD. Only present if you own the run AND are paying for platform usage (Pay-Per-Usage, Rental, or Pay-Per-Event with usage costs like standby Actors). Not available for standard Pay-Per-Event Actors. Requires authentication token to access.

    * anyOf
      * RunUsageUsd
      * null
      **ACTOR\_COMPUTE\_UNITS** number | null nullable\
      **Example:** `0.0003`
    * **DATASET\_READS** number | null nullable\
      **Example:** `0.0001`
    * **DATASET\_WRITES** number | null nullable\
      **Example:** `0.0001`
    * **KEY\_VALUE\_STORE\_READS** number | null nullable\
      **Example:** `0.0001`
    * **KEY\_VALUE\_STORE\_WRITES** number | null nullable\
      **Example:** `0.00005`
    * **KEY\_VALUE\_STORE\_LISTS** number | null nullable\
      **Example:** `0.0001`
    * **REQUEST\_QUEUE\_READS** number | null nullable\
      **Example:** `0.0001`
    * **REQUEST\_QUEUE\_WRITES** number | null nullable\
      **Example:** `0.0001`
    * **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
      **Example:** `0.001`
    * **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
      **Example:** `0.003`
    * **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
      **Example:** `0.034`
    * **PROXY\_SERPS** number | null nullable\
      **Example:** `0.003`

  * **metamorphs** object

    List of metamorph events that occurred during the run.

    * anyOf

      * object\[]
      * null

      **createdAt** string\<date-time> required

      Time when the metamorph occurred.

      **Example:** `2019-11-30T07:39:24.202Z`

    * **actorId** string required

      ID of the Actor that the run was metamorphed to.

      **Example:** `nspoEjklmnsF2oosD`

    * **buildId** string required

      ID of the build used for the metamorphed Actor.

      **Example:** `ME6oKecqy5kXDS4KQ`

    * **inputKey** string | null nullable

      Key of the input record in the key-value store.

      **Example:** `INPUT-METAMORPH-1`

  * **platformUsageBillingModel** string

    Indicates which party covers platform usage costs for this run.

    **Example:** `USER`

**null**


```json
{
  "data": {
    "id": "HG7ML7M8z78YcAPEB",
    "actId": "HDSasDasz78YcAPEB",
    "userId": "7sT5jcggjjA9fNcxF",
    "actorTaskId": "KJHSKHausidyaJKHs",
    "startedAt": "2019-11-30T07:34:24.202Z",
    "finishedAt": "2019-12-12T09:30:12.202Z",
    "status": "READY",
    "statusMessage": "Actor is running",
    "isStatusMessageTerminal": false,
    "meta": {
      "origin": "DEVELOPMENT",
      "clientIp": "string",
      "userAgent": "string",
      "scheduleId": "string",
      "scheduledAt": "2024-07-29T15:51:28.071Z"
    },
    "pricingInfo": {
      "apifyMarginPercentage": 0,
      "createdAt": "2024-07-29T15:51:28.071Z",
      "startedAt": "2024-07-29T15:51:28.071Z",
      "notifiedAboutFutureChangeAt": "2024-07-29T15:51:28.071Z",
      "notifiedAboutChangeAt": "2024-07-29T15:51:28.071Z",
      "reasonForChange": "string",
      "isPriceChangeNotificationSuppressed": true,
      "forceContainsSignificantPriceChange": true,
      "pricingModel": "PAY_PER_EVENT",
      "pricingPerEvent": {
        "actorChargeEvents": {}
      },
      "minimalMaxTotalChargeUsd": 0
    },
    "stats": {
      "inputBodyLen": 240,
      "migrationCount": 0,
      "rebootCount": 0,
      "restartCount": 0,
      "resurrectCount": 2,
      "memAvgBytes": 267874071.9,
      "memMaxBytes": 404713472,
      "memCurrentBytes": 0,
      "cpuAvgUsage": 33.7532101107538,
      "cpuMaxUsage": 169.650735534941,
      "cpuCurrentUsage": 0,
      "netRxBytes": 103508042,
      "netTxBytes": 4854600,
      "durationMillis": 248472,
      "runTimeSecs": 248.472,
      "metamorph": 0,
      "computeUnits": 0.13804
    },
    "chargedEventCounts": {
      "actor-start": 1,
      "page-crawled": 150,
      "data-extracted": 75
    },
    "options": {
      "build": "latest",
      "timeoutSecs": 300,
      "memoryMbytes": 1024,
      "diskMbytes": 2048,
      "maxItems": 1000,
      "maxTotalChargeUsd": 5
    },
    "buildId": "7sT5jcggjjA9fNcxF",
    "exitCode": 0,
    "generalAccess": "RESTRICTED",
    "defaultKeyValueStoreId": "eJNzqsbPiopwJcgGQ",
    "defaultDatasetId": "wmKPijuyDnPZAPRMk",
    "defaultRequestQueueId": "FL35cSF7jrxr3BY39",
    "storageIds": {
      "datasets": {
        "default": "wmKPijuyDnPZAPRMk"
      },
      "keyValueStores": {
        "default": "eJNzqsbPiopwJcgGQ"
      },
      "requestQueues": {
        "default": "FL35cSF7jrxr3BY39"
      }
    },
    "buildNumber": "0.0.36",
    "containerUrl": "https://g8kd8kbc5ge8.runs.apify.net",
    "isContainerServerReady": true,
    "gitBranchName": "master",
    "usage": {
      "ACTOR_COMPUTE_UNITS": 3,
      "DATASET_READS": 4,
      "DATASET_WRITES": 4,
      "KEY_VALUE_STORE_READS": 5,
      "KEY_VALUE_STORE_WRITES": 3,
      "KEY_VALUE_STORE_LISTS": 5,
      "REQUEST_QUEUE_READS": 2,
      "REQUEST_QUEUE_WRITES": 1,
      "DATA_TRANSFER_INTERNAL_GBYTES": 1,
      "DATA_TRANSFER_EXTERNAL_GBYTES": 3,
      "PROXY_RESIDENTIAL_TRANSFER_GBYTES": 34,
      "PROXY_SERPS": 3
    },
    "usageTotalUsd": 0.2654,
    "usageUsd": {
      "ACTOR_COMPUTE_UNITS": 0.0003,
      "DATASET_READS": 0.0001,
      "DATASET_WRITES": 0.0001,
      "KEY_VALUE_STORE_READS": 0.0001,
      "KEY_VALUE_STORE_WRITES": 0.00005,
      "KEY_VALUE_STORE_LISTS": 0.0001,
      "REQUEST_QUEUE_READS": 0.0001,
      "REQUEST_QUEUE_WRITES": 0.0001,
      "DATA_TRANSFER_INTERNAL_GBYTES": 0.001,
      "DATA_TRANSFER_EXTERNAL_GBYTES": 0.003,
      "PROXY_RESIDENTIAL_TRANSFER_GBYTES": 0.034,
      "PROXY_SERPS": 0.003
    },
    "metamorphs": [
      {
        "createdAt": "2019-11-30T07:39:24.202Z",
        "actorId": "nspoEjklmnsF2oosD",
        "buildId": "ME6oKecqy5kXDS4KQ",
        "inputKey": "INPUT-METAMORPH-1"
      }
    ],
    "platformUsageBillingModel": "USER"
  }
}
```


**RunUsageUsd**

**Schema**

* **data** object required

  Represents an Actor run and its associated data.

  * **id** string required

    Unique identifier of the Actor run.

    **Example:** `HG7ML7M8z78YcAPEB`

  * **actId** string required

    ID of the Actor that was run.

    **Example:** `HDSasDasz78YcAPEB`

  * **userId** string required

    ID of the user who started the run.

    **Example:** `7sT5jcggjjA9fNcxF`

  * **actorTaskId** string | null nullable

    ID of the Actor task, if the run was started from a task.

    **Example:** `KJHSKHausidyaJKHs`

  * **startedAt** string\<date-time> required

    Time when the Actor run started.

    **Example:** `2019-11-30T07:34:24.202Z`

  * **finishedAt** string,null\<date-time> nullable

    Time when the Actor run finished.

    **Example:** `2019-12-12T09:30:12.202Z`

  * **status** ActorJobStatus (string) required

    Status of an Actor job (run or build).

    **Possible values:** \[`READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `TIMING-OUT`, `TIMED-OUT`, `ABORTING`, `ABORTED`]

  * **statusMessage** string | null nullable

    Detailed message about the run status.

    **Example:** `Actor is running`

  * **isStatusMessageTerminal** boolean | null nullable

    Whether the status message is terminal (final).

    **Example:** `false`

  * **meta** object required

    Metadata about the Actor run.

    * **origin** RunOrigin (string) required

      **Possible values:** \[`DEVELOPMENT`, `WEB`, `API`, `SCHEDULER`, `TEST`, `WEBHOOK`, `ACTOR`, `CLI`, `CI`, `STANDBY`]

    * **clientIp** string | null nullable

      IP address of the client that started the run.

    * **userAgent** string | null nullable

      User agent of the client that started the run.

    * **scheduleId** string | null nullable

      ID of the schedule that triggered the run.

    * **scheduledAt** string,null\<date-time> nullable

      Time when the run was scheduled.

  * **pricingInfo** object

    Pricing information for the Actor.

    * **pricingModel**

      Pricing information for the Actor.

      **Possible values:** \[`PAY_PER_EVENT`, `PRICE_PER_DATASET_ITEM`, `FLAT_PRICE_PER_MONTH`, `FREE`]
      * **PAY\_PER\_EVENT**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **pricingPerEvent** object required

          * **actorChargeEvents** object

            * **property name\*** ActorChargeEvent

              Definition of a single chargeable event for a pay-per-event Actor. Each event is either flat-priced (`eventPriceUsd` is set) or tier-priced (`eventTieredPricingUsd` is set); the two are mutually exclusive.

              * **eventTitle** string required

                Human-readable title shown to users in the billing UI.

              * **eventDescription** string required

                Human-readable description of what triggers this event.

              * **eventPriceUsd** number

                Flat price per event in USD. Present only for non-tiered events. Mutually exclusive with `eventTieredPricingUsd`.

              * **eventTieredPricingUsd** object

                Tiered price-per-event pricing for a single charge event, keyed by subscription tier (e.g. `FREE`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`). The actual price applied is resolved from the user's tier.

                * **property name\*** TieredPricingPerEventEntry

                  A single tier's price-per-event entry.

                  * **tieredEventPriceUsd** number required

                    Price per event in USD for this tier.

              * **isPrimaryEvent** boolean

                Whether this event is the Actor's primary chargeable event.

              * **isOneTimeEvent** boolean

                Whether this event can only be charged once per Actor run.

        * **minimalMaxTotalChargeUsd** number | null nullable

      * **PRICE\_PER\_DATASET\_ITEM**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **unitName** string required

          Name of the unit that is being charged

        * **pricePerUnitUsd** number

          Price per unit in USD. Mutually exclusive with `tieredPricing` - exactly one of the two is present on a pricing record.

        * **tieredPricing** object

          Tiered price-per-dataset-item pricing, keyed by subscription tier (e.g. `FREE`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`). The actual price applied to a run is resolved from the user's tier.

          * **property name\*** TieredPricingPerDatasetItemEntry

            A single tier's price-per-dataset-item entry.

            * **tieredPricePerUnitUsd** number required

              Price per unit in USD for this tier.

      * **FLAT\_PRICE\_PER\_MONTH**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

        * **trialMinutes** integer required

          For how long this Actor can be used for free in trial period

        * **pricePerUnitUsd** number required

          Monthly flat price in USD

      * **FREE**

        * **apifyMarginPercentage** number required

          In \[0, 1], fraction of pricePerUnitUsd that goes to Apify

        * **createdAt** string\<date-time> required

          When this pricing info record has been created

        * **startedAt** string\<date-time> required

          Since when is this pricing info record effective for a given Actor

        * **notifiedAboutFutureChangeAt** string,null\<date-time> nullable

        * **notifiedAboutChangeAt** string,null\<date-time> nullable

        * **reasonForChange** string | null nullable

        * **isPriceChangeNotificationSuppressed** boolean

        * **forceContainsSignificantPriceChange** boolean

  * **stats** object required

    Statistics of the Actor run.

    * **inputBodyLen** integer | null nullable

      **Possible values:** `>= 0`

      **Example:** `240`

    * **migrationCount** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **rebootCount** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **restartCount** integer required

      **Possible values:** `>= 0`

      **Example:** `0`

    * **resurrectCount** integer required

      **Possible values:** `>= 0`

      **Example:** `2`

    * **memAvgBytes** number\
      **Example:** `267874071.9`

    * **memMaxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `404713472`

    * **memCurrentBytes** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **cpuAvgUsage** number\
      **Example:** `33.7532101107538`

    * **cpuMaxUsage** number\
      **Example:** `169.650735534941`

    * **cpuCurrentUsage** number\
      **Example:** `0`

    * **netRxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `103508042`

    * **netTxBytes** integer

      **Possible values:** `>= 0`

      **Example:** `4854600`

    * **durationMillis** integer

      **Possible values:** `>= 0`

      **Example:** `248472`

    * **runTimeSecs** number

      **Possible values:** `>= 0`

      **Example:** `248.472`

    * **metamorph** integer

      **Possible values:** `>= 0`

      **Example:** `0`

    * **computeUnits** number required

      **Possible values:** `>= 0`

      **Example:** `0.13804`

  * **chargedEventCounts** object

    A map of charged event types to their counts. The keys are event type identifiers defined by the Actor's pricing model (pay-per-event), and the values are the number of times each event was charged during this run.

    * **property name\*** integer

  * **options** object required

    Configuration options for the Actor run.

    * **build** string required\
      **Example:** `latest`

    * **timeoutSecs** integer required

      **Possible values:** `>= 0`

      **Example:** `300`

    * **memoryMbytes** integer required

      **Possible values:** `>= 128` and `<= 32768`

      **Example:** `1024`

    * **diskMbytes** integer required

      **Possible values:** `>= 0`

      **Example:** `2048`

    * **maxItems** integer | null nullable

      **Possible values:** `>= 1`

      **Example:** `1000`

    * **maxTotalChargeUsd** number

      **Possible values:** `>= 0`

      **Example:** `5`

  * **buildId** string required

    ID of the Actor build used for this run.

    **Example:** `7sT5jcggjjA9fNcxF`

  * **exitCode** integer | null nullable

    Exit code of the Actor run process.

    **Example:** `0`

  * **generalAccess** GeneralAccess (string) required

    General access level for the Actor run.

    **Possible values:** \[`ANYONE_WITH_ID_CAN_READ`, `ANYONE_WITH_NAME_CAN_READ`, `FOLLOW_USER_SETTING`, `RESTRICTED`]

    **Example:** `RESTRICTED`

  * **defaultKeyValueStoreId** string required

    ID of the default key-value store for this run.

    **Example:** `eJNzqsbPiopwJcgGQ`

  * **defaultDatasetId** string required

    ID of the default dataset for this run.

    **Example:** `wmKPijuyDnPZAPRMk`

  * **defaultRequestQueueId** string required

    ID of the default request queue for this run.

    **Example:** `FL35cSF7jrxr3BY39`

  * **storageIds** object

    A map of aliased storage IDs associated with this run, grouped by storage type.

    * **datasets** object

      Aliased dataset IDs for this run.

      * **default** string

        ID of the default dataset for this run.

        **Example:** `wmKPijuyDnPZAPRMk`

      * **property name\*** string

    * **keyValueStores** object

      Aliased key-value store IDs for this run.

      * **default** string

        ID of the default key-value store for this run.

        **Example:** `eJNzqsbPiopwJcgGQ`

      * **property name\*** string

    * **requestQueues** object

      Aliased request queue IDs for this run.

      * **default** string

        ID of the default request queue for this run.

        **Example:** `FL35cSF7jrxr3BY39`

      * **property name\*** string

  * **buildNumber** string | null nullable

    Build number of the Actor build used for this run.

    **Possible values:** Value must match regular expression `^([0-9]|[1-9][0-9])\.([0-9]|[1-9][0-9])(\.[1-9][0-9]{0,4})$`

    **Example:** `0.0.36`

  * **containerUrl** string\<uri>

    URL of the container running the Actor.

    **Example:** `https://g8kd8kbc5ge8.runs.apify.net`

  * **isContainerServerReady** boolean | null nullable

    Whether the container's HTTP server is ready to accept requests.

    **Example:** `true`

  * **gitBranchName** string | null nullable

    Name of the git branch used for the Actor build.

    **Example:** `master`

  * **usage** object

    Resource usage statistics for the run.

    * anyOf
      * RunUsage
      * null
      **ACTOR\_COMPUTE\_UNITS** number | null nullable\
      **Example:** `3`
    * **DATASET\_READS** integer | null nullable\
      **Example:** `4`
    * **DATASET\_WRITES** integer | null nullable\
      **Example:** `4`
    * **KEY\_VALUE\_STORE\_READS** integer | null nullable\
      **Example:** `5`
    * **KEY\_VALUE\_STORE\_WRITES** integer | null nullable\
      **Example:** `3`
    * **KEY\_VALUE\_STORE\_LISTS** integer | null nullable\
      **Example:** `5`
    * **REQUEST\_QUEUE\_READS** integer | null nullable\
      **Example:** `2`
    * **REQUEST\_QUEUE\_WRITES** integer | null nullable\
      **Example:** `1`
    * **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
      **Example:** `1`
    * **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
      **Example:** `3`
    * **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
      **Example:** `34`
    * **PROXY\_SERPS** integer | null nullable\
      **Example:** `3`

  * **usageTotalUsd** number | null nullable

    Total cost in USD for this run. Represents what you actually pay. For run owners: includes platform usage (compute units) and/or event costs depending on the Actor's pricing model. For run non-owners: only available for Pay-Per-Event Actors (event costs only). Requires authentication token to access.

    **Example:** `0.2654`

  * **usageUsd** object

    Platform usage costs breakdown in USD. Only present if you own the run AND are paying for platform usage (Pay-Per-Usage, Rental, or Pay-Per-Event with usage costs like standby Actors). Not available for standard Pay-Per-Event Actors. Requires authentication token to access.

    * anyOf
      * RunUsageUsd
      * null
      **ACTOR\_COMPUTE\_UNITS** number | null nullable\
      **Example:** `0.0003`
    * **DATASET\_READS** number | null nullable\
      **Example:** `0.0001`
    * **DATASET\_WRITES** number | null nullable\
      **Example:** `0.0001`
    * **KEY\_VALUE\_STORE\_READS** number | null nullable\
      **Example:** `0.0001`
    * **KEY\_VALUE\_STORE\_WRITES** number | null nullable\
      **Example:** `0.00005`
    * **KEY\_VALUE\_STORE\_LISTS** number | null nullable\
      **Example:** `0.0001`
    * **REQUEST\_QUEUE\_READS** number | null nullable\
      **Example:** `0.0001`
    * **REQUEST\_QUEUE\_WRITES** number | null nullable\
      **Example:** `0.0001`
    * **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
      **Example:** `0.001`
    * **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
      **Example:** `0.003`
    * **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
      **Example:** `0.034`
    * **PROXY\_SERPS** number | null nullable\
      **Example:** `0.003`

  * **metamorphs** object

    List of metamorph events that occurred during the run.

    * anyOf

      * object\[]
      * null

      **createdAt** string\<date-time> required

      Time when the metamorph occurred.

      **Example:** `2019-11-30T07:39:24.202Z`

    * **actorId** string required

      ID of the Actor that the run was metamorphed to.

      **Example:** `nspoEjklmnsF2oosD`

    * **buildId** string required

      ID of the build used for the metamorphed Actor.

      **Example:** `ME6oKecqy5kXDS4KQ`

    * **inputKey** string | null nullable

      Key of the input record in the key-value store.

      **Example:** `INPUT-METAMORPH-1`

  * **platformUsageBillingModel** string

    Indicates which party covers platform usage costs for this run.

    **Example:** `USER`

**null**

* **ACTOR\_COMPUTE\_UNITS** number | null nullable\
  **Example:** `3`

* **DATASET\_READS** integer | null nullable\
  **Example:** `4`

* **DATASET\_WRITES** integer | null nullable\
  **Example:** `4`

* **KEY\_VALUE\_STORE\_READS** integer | null nullable\
  **Example:** `5`

* **KEY\_VALUE\_STORE\_WRITES** integer | null nullable\
  **Example:** `3`

* **KEY\_VALUE\_STORE\_LISTS** integer | null nullable\
  **Example:** `5`

* **REQUEST\_QUEUE\_READS** integer | null nullable\
  **Example:** `2`

* **REQUEST\_QUEUE\_WRITES** integer | null nullable\
  **Example:** `1`

* **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
  **Example:** `1`

* **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
  **Example:** `3`

* **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
  **Example:** `34`

* **PROXY\_SERPS** integer | null nullable\
  **Example:** `3`

**object\[]**

* **ACTOR\_COMPUTE\_UNITS** number | null nullable\
  **Example:** `0.0003`

* **DATASET\_READS** number | null nullable\
  **Example:** `0.0001`

* **DATASET\_WRITES** number | null nullable\
  **Example:** `0.0001`

* **KEY\_VALUE\_STORE\_READS** number | null nullable\
  **Example:** `0.0001`

* **KEY\_VALUE\_STORE\_WRITES** number | null nullable\
  **Example:** `0.00005`

* **KEY\_VALUE\_STORE\_LISTS** number | null nullable\
  **Example:** `0.0001`

* **REQUEST\_QUEUE\_READS** number | null nullable\
  **Example:** `0.0001`

* **REQUEST\_QUEUE\_WRITES** number | null nullable\
  **Example:** `0.0001`

* **DATA\_TRANSFER\_INTERNAL\_GBYTES** number | null nullable\
  **Example:** `0.001`

* **DATA\_TRANSFER\_EXTERNAL\_GBYTES** number | null nullable\
  **Example:** `0.003`

* **PROXY\_RESIDENTIAL\_TRANSFER\_GBYTES** number | null nullable\
  **Example:** `0.034`

* **PROXY\_SERPS** number | null nullable\
  **Example:** `0.003`

**null**

* **createdAt** string\<date-time> required

  Time when the metamorph occurred.

  **Example:** `2019-11-30T07:39:24.202Z`

* **actorId** string required

  ID of the Actor that the run was metamorphed to.

  **Example:** `nspoEjklmnsF2oosD`

* **buildId** string required

  ID of the build used for the metamorphed Actor.

  **Example:** `ME6oKecqy5kXDS4KQ`

* **inputKey** string | null nullable

  Key of the input record in the key-value store.

  **Example:** `INPUT-METAMORPH-1`

### Status 400

Bad request - invalid input parameters or request body.


```json
{
  "error": {
    "type": "invalid-input",
    "message": "Invalid input: The request body contains invalid data."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "invalid-input",
    "message": "Invalid input: The request body contains invalid data."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 401

Unauthorized - authentication required or invalid token.


```json
{
  "error": {
    "type": "invalid-token",
    "message": "Authentication token is not valid."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "invalid-token",
    "message": "Authentication token is not valid."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 402

Payment required - the user has exceeded their usage limit, does not have enough credits, or the request lacks authentication and payment credentials.


```json
{
  "error": {
    "type": "x402-payment-required",
    "message": "Please provide X402-PAYMENT-SIGNATURE header with the payment. See https://x402.org."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "x402-payment-required",
    "message": "Please provide X402-PAYMENT-SIGNATURE header with the payment. See https://x402.org."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 403

Forbidden - insufficient permissions to perform this action.


```json
{
  "error": {
    "type": "insufficient-permissions",
    "message": "You do not have permission to perform this action."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "insufficient-permissions",
    "message": "You do not have permission to perform this action."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 404

Not found - the requested resource does not exist.


```json
{
  "error": {
    "type": "record-not-found",
    "message": "The requested resource was not found."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "record-not-found",
    "message": "The requested resource was not found."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 405

Method not allowed.


```json
{
  "error": {
    "type": "method-not-allowed",
    "message": "This API end-point can only be accessed using the following HTTP methods: OPTIONS,GET"
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "method-not-allowed",
    "message": "This API end-point can only be accessed using the following HTTP methods: OPTIONS,GET"
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 413

Payload too large - the request body exceeds the size limit.


```json
{
  "error": {
    "type": "request-too-large",
    "message": "The POST payload is too large (limit: 9437184 bytes, actual length: 10485760 bytes)."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "request-too-large",
    "message": "The POST payload is too large (limit: 9437184 bytes, actual length: 10485760 bytes)."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 415

Unsupported media type - the Content-Encoding of the request is not supported.


```json
{
  "error": {
    "type": "unsupported-content-encoding",
    "message": "Content-Encoding \"bla\" is not supported."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "unsupported-content-encoding",
    "message": "Content-Encoding \"bla\" is not supported."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.

### Status 429

Too many requests - rate limit exceeded.


```json
{
  "error": {
    "type": "rate-limit-exceeded",
    "message": "You have exceeded the rate limit. Please try again later."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.


```json
{
  "error": {
    "type": "rate-limit-exceeded",
    "message": "You have exceeded the rate limit. Please try again later."
  }
}
```


**Schema**

* **error** object required

  * **type** ErrorType (string)

    Machine-processable error type identifier.

    **Possible values:** \[`3d-secure-auth-failed`, `access-right-already-exists`, `action-not-found`, `actor-already-rented`, `actor-can-not-be-rented`, `actor-disabled`, `actor-is-not-rented`, `actor-memory-limit-exceeded`, `actor-name-exists-new-owner`, `actor-name-not-unique`, `actor-not-found`, `actor-not-github-actor`, `actor-not-public`, `actor-permission-level-not-supported-for-agentic-payments`, `actor-review-already-exists`, `actor-run-failed`, `actor-standby-not-supported-for-agentic-payments`, `actor-task-name-not-unique`, `agentic-payment-info-retrieval-error`, `agentic-payment-information-missing`, `agentic-payment-insufficient-amount`, `agentic-payment-provider-internal-error`, `agentic-payment-provider-unauthorized`, `airtable-webhook-deprecated`, `already-subscribed-to-paid-actor`, `apify-plan-required-to-use-paid-actor`, `apify-signup-not-allowed`, `auth-method-not-supported`, `authorization-server-not-found`, `auto-issue-date-invalid`, `background-check-required`, `billing-system-error`, `black-friday-plan-expired`, `braintree-error`, `braintree-not-linked`, `braintree-operation-timed-out`, `braintree-unsupported-currency`, `build-not-found`, `build-outdated`, `cannot-add-apify-events-to-ppe-actor`, `cannot-add-multiple-pricing-infos`, `cannot-add-pricing-info-that-alters-past`, `cannot-add-second-future-pricing-info`, `cannot-build-actor-from-webhook`, `cannot-change-billing-interval`, `cannot-change-owner`, `cannot-charge-apify-event`, `cannot-charge-non-pay-per-event-actor`, `cannot-comment-as-other-user`, `cannot-copy-actor-task`, `cannot-create-payout`, `cannot-create-public-actor`, `cannot-create-tax-transaction`, `cannot-delete-critical-actor`, `cannot-delete-invoice`, `cannot-delete-paid-actor`, `cannot-disable-one-time-event-for-apify-start-event`, `cannot-disable-organization-with-enabled-members`, `cannot-disable-user-with-subscription`, `cannot-link-oauth-to-unverified-email`, `cannot-metamorph-to-pay-per-result-actor`, `cannot-modify-actor-pricing-too-frequently`, `cannot-modify-actor-pricing-with-immediate-effect`, `cannot-override-paid-actor-trial`, `cannot-permanently-delete-subscription`, `cannot-publish-actor`, `cannot-reduce-last-full-token`, `cannot-reimburse-more-than-original-charge`, `cannot-reimburse-non-rental-charge`, `cannot-remove-own-actor-from-recently-used`, `cannot-remove-payment-method`, `cannot-remove-pricing-info`, `cannot-remove-running-run`, `cannot-remove-user-with-public-actors`, `cannot-remove-user-with-subscription`, `cannot-remove-user-with-unpaid-invoice`, `cannot-rename-env-var`, `cannot-rent-paid-actor`, `cannot-review-own-actor`, `cannot-set-access-rights-for-owner`, `cannot-set-is-status-message-terminal`, `cannot-unpublish-critical-actor`, `cannot-unpublish-paid-actor`, `cannot-unpublish-profile`, `cannot-update-invoice-field`, `concurrent-runs-limit-exceeded`, `concurrent-update-detected`, `conference-token-not-found`, `content-encoding-forbidden-for-html`, `coupon-already-redeemed`, `coupon-expired`, `coupon-for-new-customers`, `coupon-for-subscribed-users`, `coupon-limits-are-in-conflict-with-current-limits`, `coupon-max-number-of-redemptions-reached`, `coupon-not-found`, `coupon-not-unique`, `coupons-disabled`, `create-github-issue-not-allowed`, `creator-plan-not-available`, `cron-expression-invalid`, `daily-ai-token-limit-exceeded`, `daily-publication-limit-exceeded`, `dataset-does-not-have-fields-schema`, `dataset-does-not-have-schema`, `dataset-locked`, `dataset-schema-invalid`, `dcr-not-supported`, `default-dataset-not-found`, `deleting-default-build`, `deleting-unfinished-build`, `email-already-taken`, `email-already-taken-removed-user`, `email-domain-not-allowed-for-coupon`, `email-invalid`, `email-not-allowed`, `email-not-valid`, `email-update-too-soon`, `elevated-permissions-needed`, `env-var-already-exists`, `exchange-rate-fetch-failed`, `expired-conference-token`, `failed-to-charge-user`, `final-invoice-negative`, `full-permission-actor-not-approved`, `github-branch-empty`, `github-issue-already-exists`, `github-public-key-not-found`, `github-repository-not-found`, `github-signature-does-not-match-payload`, `github-user-not-authorized-for-issues`, `gmail-not-allowed`, `id-does-not-match`, `incompatible-billing-interval`, `incomplete-payout-billing-info`, `inconsistent-currencies`, `incorrect-pricing-modifier-prefix`, `input-json-invalid-characters`, `input-json-not-object`, `input-json-too-long`, `input-update-collision`, `insufficient-permissions`, `insufficient-permissions-to-change-field`, `insufficient-security-measures`, `insufficient-tax-country-evidence`, `integration-auth-error`, `internal-server-error`, `invalid-billing-info`, `invalid-billing-period-for-payout`, `invalid-build`, `invalid-client-key`, `invalid-collection`, `invalid-conference-login-password`, `invalid-content-type-header`, `invalid-credentials`, `invalid-git-auth-token`, `invalid-github-issue-url`, `invalid-header`, `invalid-id`, `invalid-idempotency-key`, `invalid-input`, `invalid-input-schema`, `invalid-invoice`, `invalid-invoice-type`, `invalid-issue-date`, `invalid-label-params`, `invalid-main-account-user-id`, `invalid-oauth-app`, `invalid-oauth-scope`, `invalid-one-time-invoice`, `invalid-parameter`, `invalid-payout-status`, `invalid-picture-url`, `invalid-record-key`, `invalid-request`, `invalid-resource-type`, `invalid-signature`, `invalid-subscription-plan`, `invalid-tax-number`, `invalid-tax-number-format`, `invalid-token`, `invalid-token-type`, `invalid-two-factor-code`, `invalid-two-factor-code-or-recovery-code`, `invalid-two-factor-recovery-code`, `invalid-username`, `invalid-value`, `invitation-invalid-resource-type`, `invitation-no-longer-valid`, `invoice-canceled`, `invoice-cannot-be-refunded-due-to-too-high-amount`, `invoice-incomplete`, `invoice-is-draft`, `invoice-locked`, `invoice-must-be-buffer`, `invoice-not-canceled`, `invoice-not-draft`, `invoice-not-found`, `invoice-outdated`, `invoice-paid-already`, `issue-already-connected-to-github`, `issue-not-found`, `issues-bad-request`, `issuer-not-registered`, `job-finished`, `label-already-linked`, `last-api-token`, `limit-reached`, `max-items-must-be-greater-than-zero`, `max-metamorphs-exceeded`, `max-total-charge-usd-below-minimum`, `max-total-charge-usd-must-be-greater-than-zero`, `method-not-allowed`, `migration-disabled`, `missing-actor-rights`, `missing-api-token`, `missing-billing-info`, `missing-line-items`, `missing-payment-date`, `missing-payout-billing-info`, `missing-proxy-password`, `missing-reporting-fields`, `missing-resource-name`, `missing-settings`, `missing-username`, `monthly-usage-limit-too-low`, `more-than-one-update-not-allowed`, `multiple-records-found`, `must-be-admin`, `name-not-unique`, `next-runtime-computation-failed`, `no-columns-in-exported-dataset`, `no-payment-attempt-for-refund-found`, `no-payment-method-available`, `no-team-account-seats-available`, `non-temporary-email`, `not-enough-usage-to-run-paid-actor`, `not-implemented`, `not-supported-currencies`, `o-auth-service-already-connected`, `o-auth-service-not-connected`, `oauth-resource-access-failed`, `one-time-invoice-already-marked-paid`, `only-drafts-can-be-deleted`, `operation-canceled`, `operation-not-allowed`, `operation-timed-out`, `organization-cannot-own-itself`, `organization-role-not-found`, `overlapping-payout-billing-periods`, `own-token-required`, `page-not-found`, `param-not-one-of`, `parameter-required`, `parameters-mismatched`, `password-reset-email-already-sent`, `password-reset-token-expired`, `pay-as-you-go-without-monthly-interval`, `payment-attempt-status-message-required`, `payout-already-paid`, `payout-canceled`, `payout-invalid-state`, `payout-must-be-approved-to-be-marked-paid`, `payout-not-found`, `payout-number-already-exists`, `phone-number-invalid`, `phone-number-landline`, `phone-number-opted-out`, `phone-verification-disabled`, `platform-feature-disabled`, `price-overrides-validation-failed`, `pricing-model-not-supported`, `promotional-plan-not-available`, `proxy-auth-ip-not-unique`, `public-actor-disabled`, `query-timeout`, `quoted-price-outdated`, `rate-limit-exceeded`, `recaptcha-invalid`, `recaptcha-required`, `record-not-found`, `record-not-public`, `record-or-token-not-found`, `record-too-large`, `redirect-uri-mismatch`, `reduced-plan-not-available`, `rental-charge-already-reimbursed`, `rental-not-allowed`, `request-aborted-prematurely`, `request-handled-or-locked`, `request-id-invalid`, `request-queue-duplicate-requests`, `request-too-large`, `requested-dataset-view-does-not-exist`, `resume-token-expired`, `run-failed`, `run-input-body-not-valid-json`, `run-timeout-exceeded`, `russia-is-evil`, `same-user`, `schedule-actor-not-found`, `schedule-actor-task-not-found`, `schedule-name-not-unique`, `schema-validation`, `schema-validation-error`, `schema-validation-failed`, `sign-up-method-not-allowed`, `slack-integration-not-custom`, `socket-closed`, `socket-destroyed`, `store-schema-invalid`, `store-terms-not-accepted`, `stripe-enabled`, `stripe-generic-decline`, `stripe-not-enabled`, `stripe-not-enabled-for-user`, `tagged-build-required`, `tax-country-invalid`, `tax-number-invalid`, `tax-number-validation-failed`, `taxamo-call-failed`, `taxamo-request-failed`, `testing-error`, `token-not-provided`, `too-few-versions`, `too-many-actor-tasks`, `too-many-actors`, `too-many-labels-on-resource`, `too-many-mcp-connectors`, `too-many-o-auth-apps`, `too-many-organizations`, `too-many-requests`, `too-many-schedules`, `too-many-ui-access-keys`, `too-many-user-labels`, `too-many-values`, `too-many-versions`, `too-many-webhooks`, `unexpected-route`, `unknown-build-tag`, `unknown-payment-provider`, `unsubscribe-token-invalid`, `unsupported-actor-pricing-model-for-agentic-payments`, `unsupported-content-encoding`, `unsupported-file-type-for-issue`, `unsupported-file-type-image-expected`, `unsupported-file-type-text-or-json-expected`, `unsupported-permission`, `upcoming-subscription-bill-not-up-to-date`, `user-already-exists`, `user-already-verified`, `user-creates-organizations-too-fast`, `user-disabled`, `user-email-is-disposable`, `user-email-not-set`, `user-email-not-verified`, `user-has-no-subscription`, `user-integration-not-found`, `user-is-already-invited`, `user-is-already-organization-member`, `user-is-not-member-of-organization`, `user-is-not-organization`, `user-is-organization`, `user-is-organization-owner`, `user-is-removed`, `user-not-found`, `user-not-logged-in`, `user-not-verified`, `user-or-token-not-found`, `user-plan-not-allowed-for-coupon`, `user-problem-with-card`, `user-record-not-found`, `username-already-taken`, `username-missing`, `username-not-allowed`, `username-removal-forbidden`, `username-required`, `verification-email-already-sent`, `verification-token-expired`, `version-already-exists`, `versions-size-exceeded`, `weak-password`, `x402-agentic-payment-already-finalized`, `x402-agentic-payment-insufficient-amount`, `x402-agentic-payment-malformed-token`, `x402-agentic-payment-settlement-failed`, `x402-agentic-payment-settlement-in-progress`, `x402-agentic-payment-settlement-stuck`, `x402-agentic-payment-unauthorized`, `x402-payment-required`, `zero-invoice`]

  * **message** string

    Human-readable error message describing what went wrong.
