# API contracts

## Authentication

- `POST /auth/register` `{email,password}` -> `201 {access_token,token_type}`
- `POST /auth/login` `{email,password}` -> `{access_token,token_type}`
- `GET /auth/me` bearer auth -> user quota and profile
- `POST /internal/quota/reserve` internal key -> quota response, `403` on refusal
- `POST /internal/quota/release` internal key -> quota response

## Training

- `POST /train` multipart form fields `file, algo, task_type, target_col, ai_cleaning`; bearer auth.
- `GET /jobs/{id}` bearer auth; owner only.
- `GET /jobs` bearer auth; newest jobs first.

Job statuses: `queued`, `running`, `succeeded`, `failed`.

## Inference

- `GET /models` list caller models
- `GET /models/{id}` model metadata and cleaning plan
- `DELETE /models/{id}` permanently deletes the caller's model artifact and metadata and restores one quota slot
- `POST /predict/{id}` `{column: value}` -> `{prediction, probabilities?}`
- `POST /predict/{id}/batch` `[{column: value}, ...]` -> `{results: [{prediction, probabilities?}, ...]}`; batches are limited to 100,000 rows

## Cleaning plan

```json
{
  "columns": [
    {
      "name": "age",
      "action": "keep",
      "reason": "Numeric feature",
      "impute": "median",
      "encode": "none",
      "scale": "standard"
    }
  ],
  "row_rules": {"drop_missing_target": true}
}
```

Allowed values: actions `keep|drop`, impute `median|mean|mode|constant|none`,
encode `onehot|ordinal|none`, scale `none|standard`.

## Errors

`400` invalid CSV, `401` invalid/missing JWT, `403` quota exceeded or wrong internal key,
`404` resource not found, `409` duplicate email, `413` upload too large,
`422` invalid payload or target column, `429` rate limit exceeded.
