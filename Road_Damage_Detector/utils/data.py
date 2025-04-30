def roboflow_dataset(api_key, workspace, project_name, version_number=1, model_format="yolov8"):
    from roboflow import Roboflow
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(workspace).project(project_name)
    version = project.version(version_number)
    dataset = version.download(model_format)
    print(f"Dataset downloaded to: {dataset.location}")
    return dataset.location
