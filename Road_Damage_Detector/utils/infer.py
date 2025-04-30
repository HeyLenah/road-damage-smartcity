def predict(model, source, output_dir='/content/results', name='test_preds'):
    results = model.predict(
        source=source,
        imgsz=640,
        save=True,
        project=output_dir,
        name=name,
        exist_ok=True
    )
    return results
