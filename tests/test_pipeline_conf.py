modules = [
    "test_modules.py"
]
pipelines = [
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
                "name": "TestInitialiser",
                "params": [
                    "PASS 1",
                    "PASS 2"
                ]
            }
        ],
        "tasks": [
            {
                "name": "TestTask",
                "params": [
                    "FIRST",
                    "I"
                ]
            },
            {
                "name": "TestTask",
                "params": [
                    "SECOND",
                    "II"
                ]
            }
        ],
        "finalisers": [
            {
                "name": "TestFinaliser",
                "params": [
                    "PASS 1",
                    "PASS 2"
                ]
            }
        ]
    }
]
