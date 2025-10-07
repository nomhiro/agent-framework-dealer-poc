# サンプル在庫データ（複数の車種とグレード、エンジンオプションを含む）
SAMPLE_INVENTORY = [
    {
        "model_id": "PRIUS",
        "model_name": "プリウス",
        "vehicle_type": "ハイブリッド",
        "grades": [
            {
                "grade_id": "PRIUS-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "PRIUS-X-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2750000
                    },
                    {
                        "engine_id": "PRIUS-X-PHV",
                        "engine_type": "プラグインハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3200000
                    }
                ]
            },
            {
                "grade_id": "PRIUS-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "PRIUS-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 3200000
                    },
                    {
                        "engine_id": "PRIUS-G-PHV",
                        "engine_type": "プラグインハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3650000
                    }
                ]
            },
            {
                "grade_id": "PRIUS-Z",
                "grade_name": "Z",
                "engine_options": [
                    {
                        "engine_id": "PRIUS-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 3700000
                    },
                    {
                        "engine_id": "PRIUS-Z-PHV",
                        "engine_type": "プラグインハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 4150000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CROWN",
        "model_name": "クラウン",
        "vehicle_type": "ハイブリッドセダン",
        "grades": [
            {
                "grade_id": "CROWN-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "CROWN-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 4350000
                    }
                ]
            },
            {
                "grade_id": "CROWN-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "CROWN-X-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 9,
                        "price": 4900000
                    }
                ]
            },
            {
                "grade_id": "CROWN-RS",
                "grade_name": "RS",
                "engine_options": [
                    {
                        "engine_id": "CROWN-RS-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 10,
                        "price": 5400000
                    },
                    {
                        "engine_id": "CROWN-RS-TURBO",
                        "engine_type": "2.4Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 12,
                        "price": 5700000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "HARRIER",
        "model_name": "ハリアー",
        "vehicle_type": "SUV",
        "grades": [
            {
                "grade_id": "HARRIER-S",
                "grade_name": "S",
                "engine_options": [
                    {
                        "engine_id": "HARRIER-S-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3200000
                    },
                    {
                        "engine_id": "HARRIER-S-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3750000
                    }
                ]
            },
            {
                "grade_id": "HARRIER-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "HARRIER-G-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3580000
                    },
                    {
                        "engine_id": "HARRIER-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 4130000
                    }
                ]
            },
            {
                "grade_id": "HARRIER-Z",
                "grade_name": "Z",
                "engine_options": [
                    {
                        "engine_id": "HARRIER-Z-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 4200000
                    },
                    {
                        "engine_id": "HARRIER-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 9,
                        "price": 4750000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "ALPHARD",
        "model_name": "アルファード",
        "vehicle_type": "ミニバン",
        "grades": [
            {
                "grade_id": "ALPHARD-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "ALPHARD-G-GAS",
                        "engine_type": "2.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 12,
                        "price": 5400000
                    },
                    {
                        "engine_id": "ALPHARD-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 14,
                        "price": 6200000
                    }
                ]
            },
            {
                "grade_id": "ALPHARD-EXECUTIVE",
                "grade_name": "EXECUTIVE LOUNGE",
                "engine_options": [
                    {
                        "engine_id": "ALPHARD-EXECUTIVE-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 16,
                        "price": 8500000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "AQUA",
        "model_name": "アクア",
        "vehicle_type": "ハイブリッドコンパクト",
        "grades": [
            {
                "grade_id": "AQUA-B",
                "grade_name": "B",
                "engine_options": [
                    {
                        "engine_id": "AQUA-B-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 1980000
                    }
                ]
            },
            {
                "grade_id": "AQUA-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "AQUA-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 2230000
                    }
                ]
            },
            {
                "grade_id": "AQUA-Z",
                "grade_name": "Z",
                "engine_options": [
                    {
                        "engine_id": "AQUA-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2400000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "RAV4",
        "model_name": "RAV4",
        "vehicle_type": "SUV",
        "grades": [
            {
                "grade_id": "RAV4-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "RAV4-X-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2774000
                    },
                    {
                        "engine_id": "RAV4-X-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3344000
                    }
                ]
            },
            {
                "grade_id": "RAV4-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "RAV4-G-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 3044000
                    },
                    {
                        "engine_id": "RAV4-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3614000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "VOXY",
        "model_name": "ヴォクシー",
        "vehicle_type": "ミニバン",
        "grades": [
            {
                "grade_id": "VOXY-S",
                "grade_name": "S-G",
                "engine_options": [
                    {
                        "engine_id": "VOXY-S-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3090000
                    },
                    {
                        "engine_id": "VOXY-S-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3440000
                    }
                ]
            },
            {
                "grade_id": "VOXY-Z",
                "grade_name": "S-Z",
                "engine_options": [
                    {
                        "engine_id": "VOXY-Z-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3390000
                    },
                    {
                        "engine_id": "VOXY-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3740000
                    }
                ]
            }
        ]
    },
    # トヨタの追加車種
    {
        "model_id": "YARIS",
        "model_name": "ヤリス",
        "vehicle_type": "コンパクトカー",
        "grades": [
            {
                "grade_id": "YARIS-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "YARIS-X-GAS",
                        "engine_type": "1.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 1470000
                    }
                ]
            },
            {
                "grade_id": "YARIS-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "YARIS-G-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 1730000
                    },
                    {
                        "engine_id": "YARIS-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2020000
                    }
                ]
            },
            {
                "grade_id": "YARIS-Z",
                "grade_name": "Z",
                "engine_options": [
                    {
                        "engine_id": "YARIS-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2320000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "COROLLA",
        "model_name": "カローラ",
        "vehicle_type": "セダン",
        "grades": [
            {
                "grade_id": "COROLLA-G-X",
                "grade_name": "G-X",
                "engine_options": [
                    {
                        "engine_id": "COROLLA-G-X-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 1936000
                    }
                ]
            },
            {
                "grade_id": "COROLLA-S",
                "grade_name": "S",
                "engine_options": [
                    {
                        "engine_id": "COROLLA-S-GAS",
                        "engine_type": "1.8Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2216000
                    }
                ]
            },
            {
                "grade_id": "COROLLA-HYBRID",
                "grade_name": "HYBRID S",
                "engine_options": [
                    {
                        "engine_id": "COROLLA-HYBRID-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2530000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "LANDCRUISER",
        "model_name": "ランドクルーザー",
        "vehicle_type": "SUV",
        "grades": [
            {
                "grade_id": "LC-GX",
                "grade_name": "GX",
                "engine_options": [
                    {
                        "engine_id": "LC-GX-DIESEL",
                        "engine_type": "3.3Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 24,
                        "price": 5100000
                    }
                ]
            },
            {
                "grade_id": "LC-VX",
                "grade_name": "VX",
                "engine_options": [
                    {
                        "engine_id": "LC-VX-DIESEL",
                        "engine_type": "3.3Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 26,
                        "price": 6300000
                    }
                ]
            },
            {
                "grade_id": "LC-ZX",
                "grade_name": "ZX",
                "engine_options": [
                    {
                        "engine_id": "LC-ZX-DIESEL",
                        "engine_type": "3.3Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 28,
                        "price": 7300000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "SIENTA",
        "model_name": "シエンタ",
        "vehicle_type": "コンパクトミニバン",
        "grades": [
            {
                "grade_id": "SIENTA-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "SIENTA-X-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 1950000
                    }
                ]
            },
            {
                "grade_id": "SIENTA-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "SIENTA-G-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2340000
                    },
                    {
                        "engine_id": "SIENTA-G-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2740000
                    }
                ]
            },
            {
                "grade_id": "SIENTA-Z",
                "grade_name": "Z",
                "engine_options": [
                    {
                        "engine_id": "SIENTA-Z-HV",
                        "engine_type": "ハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3108000
                    }
                ]
            }
        ]
    },
    # ホンダ車種
    {
        "model_id": "NBOX",
        "model_name": "N-BOX",
        "vehicle_type": "軽自動車",
        "grades": [
            {
                "grade_id": "NBOX-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "NBOX-G-GAS",
                        "engine_type": "0.66Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 1648000
                    }
                ]
            },
            {
                "grade_id": "NBOX-L",
                "grade_name": "L",
                "engine_options": [
                    {
                        "engine_id": "NBOX-L-GAS",
                        "engine_type": "0.66Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 3,
                        "price": 1528000
                    }
                ]
            },
            {
                "grade_id": "NBOX-CUSTOM-TURBO",
                "grade_name": "Custom Turbo",
                "engine_options": [
                    {
                        "engine_id": "NBOX-CUSTOM-TURBO-GAS",
                        "engine_type": "0.66Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 2068000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "FIT",
        "model_name": "フィット",
        "vehicle_type": "コンパクトカー",
        "grades": [
            {
                "grade_id": "FIT-BASIC",
                "grade_name": "BASIC",
                "engine_options": [
                    {
                        "engine_id": "FIT-BASIC-GAS",
                        "engine_type": "1.3Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 1592000
                    }
                ]
            },
            {
                "grade_id": "FIT-HOME",
                "grade_name": "HOME",
                "engine_options": [
                    {
                        "engine_id": "FIT-HOME-GAS",
                        "engine_type": "1.3Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 1718000
                    },
                    {
                        "engine_id": "FIT-HOME-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2117000
                    }
                ]
            },
            {
                "grade_id": "FIT-LUXE",
                "grade_name": "LUXE",
                "engine_options": [
                    {
                        "engine_id": "FIT-LUXE-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2327000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "VEZEL",
        "model_name": "ヴェゼル",
        "vehicle_type": "コンパクトSUV",
        "grades": [
            {
                "grade_id": "VEZEL-G",
                "grade_name": "G",
                "engine_options": [
                    {
                        "engine_id": "VEZEL-G-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2399000
                    }
                ]
            },
            {
                "grade_id": "VEZEL-X",
                "grade_name": "X",
                "engine_options": [
                    {
                        "engine_id": "VEZEL-X-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2658000
                    }
                ]
            },
            {
                "grade_id": "VEZEL-PLaY",
                "grade_name": "PLaY",
                "engine_options": [
                    {
                        "engine_id": "VEZEL-PLaY-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3298000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "STEPWGN",
        "model_name": "ステップワゴン",
        "vehicle_type": "ミニバン",
        "grades": [
            {
                "grade_id": "STEPWGN-AIR",
                "grade_name": "AIR",
                "engine_options": [
                    {
                        "engine_id": "STEPWGN-AIR-GAS",
                        "engine_type": "1.5Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2998000
                    }
                ]
            },
            {
                "grade_id": "STEPWGN-SPADA",
                "grade_name": "SPADA",
                "engine_options": [
                    {
                        "engine_id": "STEPWGN-SPADA-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3462000
                    }
                ]
            },
            {
                "grade_id": "STEPWGN-PREMIUM",
                "grade_name": "PREMIUM LINE",
                "engine_options": [
                    {
                        "engine_id": "STEPWGN-PREMIUM-HV",
                        "engine_type": "e:HEVハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 9,
                        "price": 3841000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CIVIC",
        "model_name": "シビック",
        "vehicle_type": "セダン",
        "grades": [
            {
                "grade_id": "CIVIC-LX",
                "grade_name": "LX",
                "engine_options": [
                    {
                        "engine_id": "CIVIC-LX-GAS",
                        "engine_type": "1.5Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 3190000
                    }
                ]
            },
            {
                "grade_id": "CIVIC-EX",
                "grade_name": "EX",
                "engine_options": [
                    {
                        "engine_id": "CIVIC-EX-GAS",
                        "engine_type": "1.5Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 3539000
                    }
                ]
            },
            {
                "grade_id": "CIVIC-TYPE-R",
                "grade_name": "TYPE R",
                "engine_options": [
                    {
                        "engine_id": "CIVIC-TYPE-R-TURBO",
                        "engine_type": "2.0Lターボ",
                        "orderable": True,
                        "lead_time_weeks": 12,
                        "price": 4997000
                    }
                ]
            }
        ]
    },
    # マツダ車種
    {
        "model_id": "MAZDA2",
        "model_name": "MAZDA2",
        "vehicle_type": "コンパクトカー",
        "grades": [
            {
                "grade_id": "MAZDA2-15S",
                "grade_name": "15S",
                "engine_options": [
                    {
                        "engine_id": "MAZDA2-15S-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 1595000
                    }
                ]
            },
            {
                "grade_id": "MAZDA2-15S-PROACTIVE",
                "grade_name": "15S PROACTIVE",
                "engine_options": [
                    {
                        "engine_id": "MAZDA2-15S-PROACTIVE-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 4,
                        "price": 1826000
                    }
                ]
            },
            {
                "grade_id": "MAZDA2-15S-LPACKAGE",
                "grade_name": "15S L Package",
                "engine_options": [
                    {
                        "engine_id": "MAZDA2-15S-LPACKAGE-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2046000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "MAZDA3",
        "model_name": "MAZDA3",
        "vehicle_type": "セダン/ハッチバック",
        "grades": [
            {
                "grade_id": "MAZDA3-15S",
                "grade_name": "15S",
                "engine_options": [
                    {
                        "engine_id": "MAZDA3-15S-GAS",
                        "engine_type": "1.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2229000
                    }
                ]
            },
            {
                "grade_id": "MAZDA3-20S",
                "grade_name": "20S",
                "engine_options": [
                    {
                        "engine_id": "MAZDA3-20S-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2504000
                    }
                ]
            },
            {
                "grade_id": "MAZDA3-X-SKYACTIV",
                "grade_name": "X SKYACTIV-X",
                "engine_options": [
                    {
                        "engine_id": "MAZDA3-X-SKYACTIV-GAS",
                        "engine_type": "2.0L SKYACTIV-X",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3329000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CX3",
        "model_name": "CX-3",
        "vehicle_type": "コンパクトSUV",
        "grades": [
            {
                "grade_id": "CX3-20S",
                "grade_name": "20S",
                "engine_options": [
                    {
                        "engine_id": "CX3-20S-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 5,
                        "price": 2127000
                    }
                ]
            },
            {
                "grade_id": "CX3-XD",
                "grade_name": "XD",
                "engine_options": [
                    {
                        "engine_id": "CX3-XD-DIESEL",
                        "engine_type": "1.8Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2460000
                    }
                ]
            },
            {
                "grade_id": "CX3-XD-LPACKAGE",
                "grade_name": "XD L Package",
                "engine_options": [
                    {
                        "engine_id": "CX3-XD-LPACKAGE-DIESEL",
                        "engine_type": "1.8Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2840000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CX5",
        "model_name": "CX-5",
        "vehicle_type": "SUV",
        "grades": [
            {
                "grade_id": "CX5-20S",
                "grade_name": "20S",
                "engine_options": [
                    {
                        "engine_id": "CX5-20S-GAS",
                        "engine_type": "2.0Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 2902000
                    }
                ]
            },
            {
                "grade_id": "CX5-25S",
                "grade_name": "25S",
                "engine_options": [
                    {
                        "engine_id": "CX5-25S-GAS",
                        "engine_type": "2.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 6,
                        "price": 3083000
                    }
                ]
            },
            {
                "grade_id": "CX5-XD",
                "grade_name": "XD",
                "engine_options": [
                    {
                        "engine_id": "CX5-XD-DIESEL",
                        "engine_type": "2.2Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3239000
                    }
                ]
            },
            {
                "grade_id": "CX5-XD-LPACKAGE",
                "grade_name": "XD L Package",
                "engine_options": [
                    {
                        "engine_id": "CX5-XD-LPACKAGE-DIESEL",
                        "engine_type": "2.2Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3892000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CX60",
        "model_name": "CX-60",
        "vehicle_type": "SUV",
        "grades": [
            {
                "grade_id": "CX60-25S",
                "grade_name": "25S",
                "engine_options": [
                    {
                        "engine_id": "CX60-25S-GAS",
                        "engine_type": "2.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 2994000
                    }
                ]
            },
            {
                "grade_id": "CX60-XD",
                "grade_name": "XD",
                "engine_options": [
                    {
                        "engine_id": "CX60-XD-DIESEL",
                        "engine_type": "3.3Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 9,
                        "price": 4620000
                    }
                ]
            },
            {
                "grade_id": "CX60-PHV",
                "grade_name": "PHEV",
                "engine_options": [
                    {
                        "engine_id": "CX60-PHV-PHEV",
                        "engine_type": "プラグインハイブリッド",
                        "orderable": True,
                        "lead_time_weeks": 10,
                        "price": 5390000
                    }
                ]
            }
        ]
    },
    {
        "model_id": "CX8",
        "model_name": "CX-8",
        "vehicle_type": "3列SUV",
        "grades": [
            {
                "grade_id": "CX8-25S",
                "grade_name": "25S",
                "engine_options": [
                    {
                        "engine_id": "CX8-25S-GAS",
                        "engine_type": "2.5Lガソリン",
                        "orderable": True,
                        "lead_time_weeks": 7,
                        "price": 3099000
                    }
                ]
            },
            {
                "grade_id": "CX8-XD",
                "grade_name": "XD",
                "engine_options": [
                    {
                        "engine_id": "CX8-XD-DIESEL",
                        "engine_type": "2.2Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 8,
                        "price": 3689000
                    }
                ]
            },
            {
                "grade_id": "CX8-XD-LPACKAGE",
                "grade_name": "XD L Package",
                "engine_options": [
                    {
                        "engine_id": "CX8-XD-LPACKAGE-DIESEL",
                        "engine_type": "2.2Lディーゼル",
                        "orderable": True,
                        "lead_time_weeks": 9,
                        "price": 4619000
                    }
                ]
            }
        ]
    }
]