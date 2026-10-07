from policy_assistant.intent import IntentClassifier


def test_training_beats_baseline(intents_df):
    clf = IntentClassifier()
    report = clf.train(intents_df)
    # 4 balanced classes -> random guessing is ~25%
    assert report.test_accuracy >= 0.6
    assert set(report.best_params) == set(IntentClassifier.PARAM_GRID)


def test_save_and_load_roundtrip(intents_df, tmp_path):
    clf = IntentClassifier()
    clf.train(intents_df)
    path = tmp_path / "intent.joblib"
    clf.save(path)
    loaded = IntentClassifier.load(path)
    q = "how do i cancel my policy"
    assert loaded.predict(q) == clf.predict(q)
