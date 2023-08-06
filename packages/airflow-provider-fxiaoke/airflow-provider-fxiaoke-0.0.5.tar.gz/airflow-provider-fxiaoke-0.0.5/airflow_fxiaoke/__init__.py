def get_provider_info():
    return {
        "package-name": "airflow-provider-fxiaoke",
        "name": "Fxiaoke Provider", # Required
        "description": "Fxiaoke for airflow providers.", # Required
        "hook-class-names": ["airflow_fxiaoke.hooks.query.FxiaokeHooks"],
        "versions": ["0.0.1"] # Required
    }