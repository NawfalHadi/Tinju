ACTIONS = [
    "Idle", "Guard", "Jab", "Low_Jab", "Straight", "Low_Straight",
    "Left_Hook", "Right_Hook", "Left_BodyHook", "Right_BodyHook",
    "Left_Uppercut", "Right_Uppercut", "Slip_Left", "Slip_Right", 
    "Guard_LeftBody", "Guard_RightBody", "Duck"
]

ACTIONS_EFFECTS = {
    "Idle": {
        "stamina_cost": 0,
        "health_recovery": 0.5,
        "stamina_recovery": 10,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0

        },
        "point_training": {
            "Idle": 20, "Jab": -10, "Low_Jab": -12, "Straight": -10, "Low_Straight": -12,
            "Left_Hook": -15, "Left_BodyHook": -15, "Right_Hook": -15, "Right_BodyHook": -15,
            "Left_Uppercut": 20, "Right_Uppercut": -20, "Guard": 20, "Slip_Left": 20,
            "Slip_Right": 20, "Duck": 30, "Guard_LeftBody": 30, "Guard_RightBody": 30
        },
    },
    "Jab": {
        "stamina_cost": 20,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 5, "Jab": 8, "Low_Jab": 3, "Straight": 0, "Low_Straight": 3, 
            "Left_Hook": 3, "Left_BodyHook": 0, "Right_Hook": 5, "Right_BodyHook": 0, 
            "Left_Uppercut": 7, "Right_Uppercut": 8, "Guard": 1, "Slip_Left": 3, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 1
        },
        "point_training": {
            "Idle": 10, "Jab": 5, "Low_Jab": 8, "Straight": 5, "Low_Straight": 8,
            "Left_Hook": 5, "Left_BodyHook": -10, "Right_Hook": 5, "Right_BodyHook": -10,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": -5,
            "Slip_Right": 3, "Duck": -3, "Guard_LeftBody": 2, "Guard_RightBody": 10
        },
    },
    "Low_Jab": {
        "stamina_cost": 25,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 4, "Jab": 8, "Low_Jab": 5, "Straight": 7, "Low_Straight": 4, 
            "Left_Hook": 5, "Left_BodyHook": 8, "Right_Hook": 5, "Right_BodyHook": 8, 
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 3, 
            "Slip_Right": 1, "Duck":5, "Guard_LeftBody": 1, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 15, "Straight": 5, "Low_Straight": 15,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": 5, "Right_BodyHook": -15,
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 15, "Slip_Left": 5,
            "Slip_Right": 10, "Duck": 15, "Guard_LeftBody": 20, "Guard_RightBody": 20
        },
    },
    "Straight": {
        "stamina_cost": 30,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 7, "Jab": 10, "Low_Jab": 0, "Straight": 8, "Low_Straight": 0, 
            "Left_Hook": 5, "Left_BodyHook": 0, "Right_Hook": 5, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 3, "Slip_Left": 0, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 3, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 10, "Jab": -10, "Low_Jab": -10, "Straight": -15, "Low_Straight": 5,
            "Left_Hook": -15, "Left_BodyHook": 5, "Right_Hook": -15, "Right_BodyHook": 5,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 8, "Slip_Left": 5,
            "Slip_Right": -5, "Duck": -10, "Guard_LeftBody": 10, "Guard_RightBody": 2
        },
    },
    "Low_Straight": {
        "stamina_cost": 35,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 6, "Jab": 10, "Low_Jab": 10, "Straight": 10, "Low_Straight": 10, 
            "Left_Hook": 10, "Left_BodyHook": 6, "Right_Hook": 8, "Right_BodyHook": 6, 
            "Left_Uppercut": 8, "Right_Uppercut": 8, "Guard": 7, "Slip_Left": 0, 
            "Slip_Right": 5, "Duck":0, "Guard_LeftBody": 7, "Guard_RightBody": 3
        },
        "point_training": {
            "Idle": 5, "Jab": 10, "Low_Jab": 10, "Straight": 15, "Low_Straight": 15,
            "Left_Hook": 15, "Left_BodyHook": -5, "Right_Hook": 10, "Right_BodyHook": -15,
            "Left_Uppercut": 10, "Right_Uppercut": 20, "Guard": 25, "Slip_Left": 15,
            "Slip_Right": -5, "Duck": 15, "Guard_LeftBody": 20, "Guard_RightBody": 20
        },
    },
    "Left_Hook": {
        "stamina_cost": 30,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 8, "Jab": 12, "Low_Jab": 0, "Straight": 10, "Low_Straight": 0, 
            "Left_Hook": 7, "Left_BodyHook": 0, "Right_Hook": 7, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 5, 
            "Slip_Right": 5, "Duck":0, "Guard_LeftBody": 3, "Guard_RightBody": 8
        },
        "point_training": {
            "Idle": 15, "Jab": 5, "Low_Jab": 15, "Straight": 10, "Low_Straight": 15,
            "Left_Hook": -5, "Left_BodyHook": 5, "Right_Hook": -15, "Right_BodyHook": 5,
            "Left_Uppercut": 20, "Right_Uppercut": 15, "Guard": 10, "Slip_Left": 2,
            "Slip_Right": -5, "Duck": -10, "Guard_LeftBody": 5, "Guard_RightBody": 5
        },
    },
    "Left_BodyHook":{
        "stamina_cost": 40,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 7, "Jab": 13, "Low_Jab": 15, "Straight": 15, "Low_Straight": 10, 
            "Left_Hook": 7, "Left_BodyHook": 15, "Right_Hook": 10, "Right_BodyHook": 15, 
            "Left_Uppercut": 15, "Right_Uppercut": 10, "Guard": 10, "Slip_Left": 10, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 7
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": -10, "Low_Straight": -15,
            "Left_Hook": 5, "Left_BodyHook": 15, "Right_Hook": -10, "Right_BodyHook": 5,
            "Left_Uppercut": 10, "Right_Uppercut": -15, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 2, "Duck": -5, "Guard_LeftBody": 20, "Guard_RightBody": 5
        },
    },
    "Right_Hook": {
        "stamina_cost": 40,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 10, "Jab": 15, "Low_Jab": 0, "Straight": 15, "Low_Straight": 0, 
            "Left_Hook": 15, "Left_BodyHook": 15, "Right_Hook": 7, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 7, "Guard": 5, "Slip_Left": 5, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 5, "Jab": 5, "Low_Jab": 5, "Straight": -15, "Low_Straight": 5,
            "Left_Hook": -15, "Left_BodyHook": -10, "Right_Hook": 10, "Right_BodyHook": -20,
            "Left_Uppercut": 15, "Right_Uppercut": 5, "Guard": 10, "Slip_Left": 3,
            "Slip_Right": -5, "Duck": 5, "Guard_LeftBody": 2, "Guard_RightBody": 10
        },
    },
    "Right_BodyHook" : {
        "stamina_cost": 45,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 9, "Jab": 17, "Low_Jab": 15, "Straight": 20, "Low_Straight": 15, 
            "Left_Hook": 15, "Left_BodyHook": 10, "Right_Hook": 20, "Right_BodyHook": 15, 
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 10, "Slip_Left": 7, 
            "Slip_Right": 10, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 5, "Jab": 10, "Low_Jab": 5, "Straight": -10, "Low_Straight": 5,
            "Left_Hook": -10, "Left_BodyHook": 10, "Right_Hook": 5, "Right_BodyHook": 20,
            "Left_Uppercut": -15, "Right_Uppercut": 15, "Guard": 5, "Slip_Left": 3,
            "Slip_Right": -10, "Duck": 10, "Guard_LeftBody": 5, "Guard_RightBody": 15
        },
    },
    "Left_Uppercut": {
        "stamina_cost": 50,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 20, "Jab": 18, "Low_Jab": 0, "Straight": 15, "Low_Straight": 0, 
            "Left_Hook": 15, "Left_BodyHook": 0, "Right_Hook": 15, "Right_BodyHook": 0, 
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 8, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 30, "Jab": 15, "Low_Jab": 15, "Straight": 10, "Low_Straight": 10,
            "Left_Hook": 15, "Left_BodyHook": 15, "Right_Hook": 10, "Right_BodyHook": -5,
            "Left_Uppercut": 25, "Right_Uppercut": 10, "Guard": 3, "Slip_Left": -5,
            "Slip_Right": -5, "Duck": -5, "Guard_LeftBody": 3, "Guard_RightBody": -5
        },
    },
    "Right_Uppercut":{
        "stamina_cost": 50,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 30, "Jab": 25, "Low_Jab": 0, "Straight": 25, "Low_Straight": 0, 
            "Left_Hook": 25, "Left_BodyHook": 0, "Right_Hook": 20, "Right_BodyHook": 0, 
            "Left_Uppercut": 20, "Right_Uppercut": 20, "Guard": 10, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 30, "Jab": 10, "Low_Jab": 15, "Straight": 5, "Low_Straight": -5,
            "Left_Hook": 15, "Left_BodyHook": 10, "Right_Hook": 10, "Right_BodyHook": 5,
            "Left_Uppercut": 15, "Right_Uppercut": 25, "Guard": 3, "Slip_Left": -5,
            "Slip_Right": -5, "Duck": -5, "Guard_LeftBody": 3, "Guard_RightBody": 15
        },        
    },
    "Guard" : {
        "stamina_cost": 0,
        "health_recovery": 0.1,
        "stamina_recovery": 5,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 15, "Jab": 10, "Low_Jab": -10, "Straight": 10, "Low_Straight": -10,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": 5, "Right_BodyHook": -15,
            "Left_Uppercut": 2, "Right_Uppercut": 2, "Guard": 20, "Slip_Left": 25,
            "Slip_Right": 25, "Duck": 30, "Guard_LeftBody": 30, "Guard_RightBody": 30
        },
    },
    "Slip_Left" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": -5, "Low_Straight": 5,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": -3, "Right_BodyHook": -10,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 10, "Duck": 10, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
    },
    "Slip_Right" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": 5, "Low_Straight": 5,
            "Left_Hook": -5, "Left_BodyHook": -10, "Right_Hook": -3, "Right_BodyHook": -15,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 10, "Duck": 10, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
    },
    "Duck" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": -5, "Straight": 15, "Low_Straight": -5,
            "Left_Hook": 20, "Left_BodyHook": -10, "Right_Hook": 20, "Right_BodyHook": -10,
            "Left_Uppercut": 25, "Right_Uppercut": 25, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 3, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
    "Guard_LeftBody" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 5, "Low_Jab": -5, "Straight": -10, "Low_Straight": 10,
            "Left_Hook": 10, "Left_BodyHook": -10, "Right_Hook": -15, "Right_BodyHook": 15,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 5, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
    "Guard_RightBody" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": -5, "Low_Jab": 5, "Straight": 5, "Low_Straight": -10,
            "Left_Hook": -10, "Left_BodyHook": 10, "Right_Hook": 15, "Right_BodyHook": -15,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 5, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
      
}