CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    model TEXT NOT NULL,
    features JSONB NOT NULL,
    prediction DOUBLE PRECISION NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS predictions_model_created_idx
    ON predictions (model, created_at DESC);
