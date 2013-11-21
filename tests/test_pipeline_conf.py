spec = {
    "modules": [
        "../tests/test_modules.py"
    ],
    "pipelines": [
        {
            "name": "TestPipeline",
            "controller": {
                "name": "TestController",
                "params": [
                    3
                ]
            },
            "initialisers": [
                {
                    "name": "EmptyInitialiser"
                }
            ],
            "tasks": [
                {
                    "name": "TestTask",
                    "params": [
                        "TASK 1",
                        "TASK 2"
                    ]
                },
                {
                    "name": "TestTask",
                    "params": [
                        "TASK 3",
                        "TASK 4"
                    ]
                }
            ],
            "finalisers": [
                {
                    "name": "TestTask",
                    "params": [
                        "FINAL 1",
                        "FINAL 2"
                    ]
                }
            ]
        }
    ]
}
