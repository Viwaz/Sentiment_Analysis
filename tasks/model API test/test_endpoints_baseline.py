import requests
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing GET /health...")
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    health_data = r.json()
    print("Health response:", json.dumps(health_data, indent=2))
    assert health_data["status"] == "ok", "Expected status 'ok'"
    assert health_data["model_loaded"] is True, "Expected model_loaded to be True"
    assert health_data["active_model_reference"] == "baseline", "Expected active model to be baseline"

    print("\nTesting GET /model-info...")
    r = requests.get(f"{base_url}/model-info")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    info_data = r.json()
    print("Model Info response:", json.dumps(info_data, indent=2))
    assert info_data["active_model_reference"] == "baseline"
    assert "model_name" in info_data
    assert "model_version" in info_data
    assert info_data["model_family"] == "classical_ml"
    assert info_data["labels"] == ["negative", "neutral", "positive"]

    print("\nTesting POST /predict...")
    payload = {
        "id": "1",
        "text": "optional original text",
        "cleaned_text": "imihigo myiza cyane"
    }
    r = requests.post(f"{base_url}/predict", json=payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    pred_data = r.json()
    print("Prediction response:", json.dumps(pred_data, indent=2))
    assert pred_data["id"] == "1"
    assert pred_data["cleaned_text"] == "imihigo myiza cyane"
    assert pred_data["predicted_label"] in ["negative", "neutral", "positive"]
    assert "predicted_confidence" in pred_data
    assert "score_negative" in pred_data
    assert "score_neutral" in pred_data
    assert "score_positive" in pred_data
    assert pred_data["model_family"] == "classical_ml"

    print("\nTesting POST /predict-batch...")
    batch_payload = {
        "records": [
            {"id": "1", "cleaned_text": "imihigo myiza cyane"},
            {"id": "2", "cleaned_text": "turaje murakoze"}
        ]
    }
    r = requests.post(f"{base_url}/predict-batch", json=batch_payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    batch_data = r.json()
    print("Batch Prediction response:", json.dumps(batch_data, indent=2))
    assert len(batch_data["predictions"]) == 2
    assert batch_data["predictions"][0]["id"] == "1"
    assert batch_data["predictions"][1]["id"] == "2"

    print("\nAll baseline endpoints verified successfully!")

if __name__ == "__main__":
    time.sleep(1)
    test_endpoints()
