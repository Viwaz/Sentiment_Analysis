---
title: Get list of datasets
url: https://docs.apify.com/api/v2/datasets-get.md
parents:
  - [Apify documentation](https://docs.apify.com/llms.txt)
  - [Apify API documentation](https://docs.apify.com/api.md)
  - [Apify API](https://docs.apify.com/api/v2.md)
  - [Datasets - Introduction](https://docs.apify.com/api/v2/storage-datasets.md)
previous: [Datasets - Introduction](https://docs.apify.com/api/v2/storage-datasets.md)
next: [Create dataset](https://docs.apify.com/api/v2/datasets-post.md)
---

# Get list of datasets


```
GET 
https://api.apify.com/v2/datasets
```


Lists all of a user's datasets.

The response is a JSON array of objects, where each object contains basic information about one dataset.

By default, the objects are sorted by the `createdAt` field in ascending order, therefore you can use pagination to incrementally fetch all datasets while new ones are still being created. To sort them in descending order, use `desc=1` parameter. The endpoint supports pagination using `limit` and `offset` parameters and it will not return more than 1000 array elements.

## Request

### Query Parameters

* **offset** double

  Number of items that should be skipped at the start. The default value is `0`.

  **Example:** `0`

  **limit** double

  Maximum number of items to return. The default value as well as the maximum is `1000`.

  **Example:** `1000`

  **desc** boolean

  If `true` or `1` then the objects are sorted by the `createdAt` field in descending order. By default, they are sorted in ascending order.

  **Example:** `true`

  **unnamed** boolean

  If `true` or `1` then all the storages are returned. By default, only named storages are returned.

  **Example:** `true`

  **ownership** StorageOwnership

  **Possible values:** \[`ownedByMe`, `sharedWithMe`]

  Filter by ownership. If this parameter is omitted, all accessible datasets are returned.
  * `ownedByMe`: Return only datasets owned by the user.
  * `sharedWithMe`: Return only datasets shared with the user by other users.
  **Example:** `ownedByMe`

<!-- -->

### Status 200

**Response Headers**




```json
{
  "data": {
    "total": 1,
    "offset": 0,
    "limit": 1000,
    "desc": false,
    "count": 1,
    "unnamed": false,
    "items": [
      {
        "id": "WkzbQMuFYuamGv3YF",
        "name": "d7b9MDYsbtX5L7XAj",
        "userId": "tbXmWu7GCxnyYtSiL",
        "createdAt": "2019-12-12T07:34:14.202Z",
        "modifiedAt": "2019-12-13T08:36:13.202Z",
        "accessedAt": "2019-12-14T08:36:13.202Z",
        "itemCount": 7,
        "cleanItemCount": 5,
        "actId": "zdc3Pyhyz3m8vjDeM",
        "actRunId": "HG7ML7M8z78YcAPEB",
        "title": "My Dataset",
        "username": "janedoe",
        "generalAccess": "RESTRICTED",
        "stats": {
          "readCount": 22,
          "writeCount": 3,
          "storageBytes": 783,
          "inflatedBytes": 0
        }
      }
    ]
  }
}
```


**Schema**

* **data** object required

  Common pagination fields for list responses.

  * **total** integer required

    The total number of items available across all pages.

    **Possible values:** `>= 0`

    **Example:** `1`

  * **offset** integer required

    The starting position for this page of results.

    **Possible values:** `>= 0`

    **Example:** `0`

  * **limit** integer required

    The maximum number of items returned per page.

    **Possible values:** `>= 1`

    **Example:** `1000`

  * **desc** boolean required

    Whether the results are sorted in descending order.

    **Example:** `false`

  * **count** integer required

    The number of items returned in this response.

    **Possible values:** `>= 0`

    **Example:** `1`

  * **unnamed** boolean

    Whether the listing was filtered to only unnamed datasets.

    **Example:** `false`

  * **items** object\[] required

    * **id** string required\
      **Example:** `WkzbQMuFYuamGv3YF`

    * **name** string required\
      **Example:** `d7b9MDYsbtX5L7XAj`

    * **userId** string required\
      **Example:** `tbXmWu7GCxnyYtSiL`

    * **createdAt** string\<date-time> required\
      **Example:** `2019-12-12T07:34:14.202Z`

    * **modifiedAt** string\<date-time> required\
      **Example:** `2019-12-13T08:36:13.202Z`

    * **accessedAt** string\<date-time> required\
      **Example:** `2019-12-14T08:36:13.202Z`

    * **itemCount** integer required\
      **Example:** `7`

    * **cleanItemCount** integer required\
      **Example:** `5`

    * **actId** string | null nullable\
      **Example:** `zdc3Pyhyz3m8vjDeM`

    * **actRunId** string | null nullable\
      **Example:** `HG7ML7M8z78YcAPEB`

    * **title** string | null nullable\
      **Example:** `My Dataset`

    * **username** string\
      **Example:** `janedoe`

    * **generalAccess** GeneralAccess (string)

      Defines the general access level for the resource.

      **Possible values:** \[`ANYONE_WITH_ID_CAN_READ`, `ANYONE_WITH_NAME_CAN_READ`, `FOLLOW_USER_SETTING`, `RESTRICTED`]

      **Example:** `RESTRICTED`

    * **stats** object

      * **readCount** integer\
        **Example:** `22`

      * **writeCount** integer\
        **Example:** `3`

      * **storageBytes** integer

        Total storage size in bytes. Only returned by the single-dataset endpoint.

        **Example:** `783`

      * **inflatedBytes** integer

        Uncompressed size in bytes. Only returned by the dataset list endpoint.

        **Example:** `0`


```json
{
  "data": {
    "total": 1,
    "offset": 0,
    "limit": 1000,
    "desc": false,
    "count": 1,
    "unnamed": false,
    "items": [
      {
        "id": "WkzbQMuFYuamGv3YF",
        "name": "d7b9MDYsbtX5L7XAj",
        "userId": "tbXmWu7GCxnyYtSiL",
        "createdAt": "2019-12-12T07:34:14.202Z",
        "modifiedAt": "2019-12-13T08:36:13.202Z",
        "accessedAt": "2019-12-14T08:36:13.202Z",
        "itemCount": 7,
        "cleanItemCount": 5,
        "actId": "zdc3Pyhyz3m8vjDeM",
        "actRunId": "HG7ML7M8z78YcAPEB",
        "title": "My Dataset",
        "username": "janedoe",
        "generalAccess": "RESTRICTED",
        "stats": {
          "readCount": 22,
          "writeCount": 3,
          "storageBytes": 783,
          "inflatedBytes": 0
        }
      }
    ]
  }
}
```


**Schema**

* **data** object required

  Common pagination fields for list responses.

  * **total** integer required

    The total number of items available across all pages.

    **Possible values:** `>= 0`

    **Example:** `1`

  * **offset** integer required

    The starting position for this page of results.

    **Possible values:** `>= 0`

    **Example:** `0`

  * **limit** integer required

    The maximum number of items returned per page.

    **Possible values:** `>= 1`

    **Example:** `1000`

  * **desc** boolean required

    Whether the results are sorted in descending order.

    **Example:** `false`

  * **count** integer required

    The number of items returned in this response.

    **Possible values:** `>= 0`

    **Example:** `1`

  * **unnamed** boolean

    Whether the listing was filtered to only unnamed datasets.

    **Example:** `false`

  * **items** object\[] required

    * **id** string required\
      **Example:** `WkzbQMuFYuamGv3YF`

    * **name** string required\
      **Example:** `d7b9MDYsbtX5L7XAj`

    * **userId** string required\
      **Example:** `tbXmWu7GCxnyYtSiL`

    * **createdAt** string\<date-time> required\
      **Example:** `2019-12-12T07:34:14.202Z`

    * **modifiedAt** string\<date-time> required\
      **Example:** `2019-12-13T08:36:13.202Z`

    * **accessedAt** string\<date-time> required\
      **Example:** `2019-12-14T08:36:13.202Z`

    * **itemCount** integer required\
      **Example:** `7`

    * **cleanItemCount** integer required\
      **Example:** `5`

    * **actId** string | null nullable\
      **Example:** `zdc3Pyhyz3m8vjDeM`

    * **actRunId** string | null nullable\
      **Example:** `HG7ML7M8z78YcAPEB`

    * **title** string | null nullable\
      **Example:** `My Dataset`

    * **username** string\
      **Example:** `janedoe`

    * **generalAccess** GeneralAccess (string)

      Defines the general access level for the resource.

      **Possible values:** \[`ANYONE_WITH_ID_CAN_READ`, `ANYONE_WITH_NAME_CAN_READ`, `FOLLOW_USER_SETTING`, `RESTRICTED`]

      **Example:** `RESTRICTED`

    * **stats** object

      * **readCount** integer\
        **Example:** `22`

      * **writeCount** integer\
        **Example:** `3`

      * **storageBytes** integer

        Total storage size in bytes. Only returned by the single-dataset endpoint.

        **Example:** `783`

      * **inflatedBytes** integer

        Uncompressed size in bytes. Only returned by the dataset list endpoint.

        **Example:** `0`

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
