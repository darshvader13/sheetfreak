requests = [
        {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': 'tt',
                        'basicChart': {
                            'chartType': 'COLUMN',
                            'legendPosition': 'BOTTOM_LEGEND',
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': 'X Axis'
                                },
                                {
                                    'position': 'LEFT_AXIS',
                                    'title': 'Y Axis'
                                }
                            ],
                            'domains': [
                                {
                                    'domain': {
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': SHEET_ID,
                                                    'startRowIndex': 0,
                                                    'endRowIndex': 10,
                                                    'startColumnIndex': 0,
                                                    'endColumnIndex': 1
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            'series': [
                                {
                                    'series': {
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': SHEET_ID,
                                                    'startRowIndex': 0,
                                                    'endRowIndex': 10,
                                                    'startColumnIndex': 1,
                                                    'endColumnIndex': 2
                                                }
                                            ]
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS',
                                    'color': {
                                        'red': 0,
                                        'green': 1,
                                        'blue': 0,
                                    }
                                }
                            ],
                        }
                    }
                }
            }
        }
    ]