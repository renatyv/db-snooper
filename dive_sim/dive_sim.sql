-- db-snooper
-- version: 0.0.4
-- generated_at_utc: 2026-07-23T08:22:07.483447Z
-- dialect: mysql
-- database: dive_sim
-- schema: dive_sim

CREATE TABLE `action_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `robot_id` int(11) NOT NULL,
  `start_time` timestamp(3) NOT NULL,
  `start_tick` int(11) NOT NULL,
  `expected_duration_s` float NOT NULL,
  `command` varchar(30) NOT NULL,
  `param1` int(11) DEFAULT NULL,
  `param2` int(11) DEFAULT NULL,
  `param3` int(11) DEFAULT NULL,
  `dist_mm` int(11) DEFAULT NULL,
  `task_id` int(11) DEFAULT NULL,
  `param4` int(11) DEFAULT NULL,
  `box_id` int(11) DEFAULT NULL,
  `param5` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `action_history_start_time_IDX` (`start_time`) USING BTREE,
  KEY `ix_action_history_robot_id_command` (`robot_id`,`command`),
  KEY `ix_action_history_task_id` (`task_id`),
  KEY `ix_action_history_robot_id_id` (`robot_id`),
  KEY `ix_action_history_command_robot_id` (`command`,`robot_id`)
) ENGINE=InnoDB AUTO_INCREMENT=600184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=60074
-- LATEST_ROWS: action_history
-- row: {"box_id": 32000259, "command": "PUT_BOX", "dist_mm": 0, "expected_duration_s": 8.40238, "id": 600183, "param1": 1130, "param2": 0, "param3": 0, "param4": 100, "param5": null, "robot_id": 7, "start_tick": 2095, "start_time": "2026-07-16T10:28:23.494000", "task_id": 197253}
-- row: {"box_id": null, "command": "MOVE", "dist_mm": 4120, "expected_duration_s": 11.1541, "id": 600182, "param1": 10, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 2076, "start_time": "2026-07-16T10:28:07.469000", "task_id": 197253}
-- row: {"box_id": 32000259, "command": "TAKE_BOX", "dist_mm": 0, "expected_duration_s": 12.5, "id": 600181, "param1": 2060, "param2": 0, "param3": 0, "param4": 100, "param5": null, "robot_id": 7, "start_tick": 2055, "start_time": "2026-07-16T10:27:50.431000", "task_id": 197253}
-- RANDOM_ROWS: action_history
-- row: {"box_id": null, "command": "ROTATE_WHEELS", "dist_mm": 0, "expected_duration_s": 2.8, "id": 590393, "param1": 2, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 1643, "start_time": "2026-07-14T13:53:21.516000", "task_id": 192654}
-- row: {"box_id": null, "command": "UNRESERVE_BOX", "dist_mm": 0, "expected_duration_s": 0.01, "id": 550714, "param1": 32000426, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 2456, "start_time": "2026-07-01T11:27:06.470000", "task_id": 188261}
-- row: {"box_id": null, "command": "MARK_PLANNABLE", "dist_mm": 0, "expected_duration_s": 0.01, "id": 566708, "param1": 7, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 454, "start_time": "2026-07-02T14:57:45.862000", "task_id": 190000}
-- row: {"box_id": null, "command": "MOVE", "dist_mm": 5834, "expected_duration_s": 13.0559, "id": 562386, "param1": 10, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 5, "start_tick": 144, "start_time": "2026-07-02T10:23:13.785000", "task_id": 189908}
-- row: {"box_id": null, "command": "TASK_START", "dist_mm": 0, "expected_duration_s": 0.01, "id": 583956, "param1": 191902, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 458, "start_time": "2026-07-09T13:26:18.292000", "task_id": 191902}
-- id: unique identifier, nulls=0, non_nulls=60074, distinct=60074
-- id numeric: min=540110, max=600183, average=570146.5000, median=570146.5000
-- robot_id: nulls=0, non_nulls=60074, distinct=3
-- robot_id numeric: min=5, max=7, average=6.0969, median=7.0000
-- robot_id values: 7=32409, 5=26585, 6=1080
-- start_time: nulls=0, non_nulls=60074, distinct=60073
-- start_time top_values: 2026-07-15 12:52:38.884000=2, 2026-06-23 12:26:15.209000=1, 2026-06-23 12:26:15.217000=1, 2026-06-23 12:26:15.225000=1, 2026-06-23 12:26:26.205000=1, 2026-06-23 12:26:26.213000=1, 2026-06-23 12:26:26.221000=1, 2026-06-23 12:26:26.279000=1, 2026-06-23 12:26:26.287000=1, 2026-06-23 12:26:34.974000=1
-- start_tick: nulls=0, non_nulls=60074, distinct=6932
-- start_tick numeric: min=1, max=9220, average=1499.3387, median=746.0000
-- expected_duration_s: nulls=0, non_nulls=60074, distinct=514
-- expected_duration_s numeric: min=0.01, max=1393.8, average=2.00622, median=0.01
-- command: nulls=0, non_nulls=60074, distinct=20
-- command top_values: TASK_START=18592, ROTATE_WHEELS=7210, TASK_DONE=6412, MARK_PLANNABLE=5026, REPLAN_ALL=5011, MOVE=4728, CHECK_PORT=3490, TAKE_BOX=1498, PUT_BOX=1475, IDLE=1090
-- param1: nulls=0, non_nulls=60074, distinct=7344
-- param1 numeric: min=-68, max=32002114, average=869892.9834, median=7.0000
-- param2: nulls=0, non_nulls=60074, distinct=121
-- param2 numeric: min=-500, max=500, average=1.5583, median=0.0000
-- param3: nulls=0, non_nulls=60074, distinct=2
-- param3 numeric: min=0, max=20, average=0.1894, median=0.0000
-- param3 values: 0=59505, 20=569
-- dist_mm: nulls=0, non_nulls=60074, distinct=322
-- dist_mm numeric: min=-28220, max=28740, average=1.8405, median=0.0000
-- task_id: nulls=0, non_nulls=60074, distinct=6986
-- task_id numeric: min=186628, max=197258, average=190983.7572, median=190364.5000
-- task_id top_values: 189607=3404, 189926=1312, 189943=936, 189921=892, 189944=505, 191351=352, 192323=156, 192160=153, 190647=144, 192320=138
-- param4: nulls=0, non_nulls=60074, distinct=2
-- param4 numeric: min=0, max=100, average=4.9489, median=0.0000
-- param4 values: 0=57101, 100=2973
-- box_id: nulls=57197, non_nulls=2877, distinct=132
-- box_id numeric: min=-1, max=32002114, average=31733721.1734, median=32000616.0000
-- param5: all NULL


CREATE TABLE `action_status_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_history_id` int(11) NOT NULL,
  `tick` int(11) NOT NULL,
  `time` timestamp(3) NOT NULL,
  `action_status` varchar(255) NOT NULL,
  `state_history_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `action_history_id` (`action_history_id`),
  KEY `state_history_id` (`state_history_id`),
  KEY `action_status_history_time_IDX` (`time`) USING BTREE,
  KEY `ix_action_status_history_status_time_action` (`action_status`,`time`,`action_history_id`),
  CONSTRAINT `action_status_history_ibfk_1` FOREIGN KEY (`action_history_id`) REFERENCES `action_history` (`id`),
  CONSTRAINT `action_status_history_ibfk_2` FOREIGN KEY (`state_history_id`) REFERENCES `robot_state_history` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1132564 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=196472
-- LATEST_ROWS: action_status_history
-- row: {"action_history_id": 600183, "action_status": "DONE", "id": 1132563, "state_history_id": 1336911, "tick": 2105, "time": "2026-07-16T10:28:33.664000"}
-- row: {"action_history_id": 600183, "action_status": "EXEC", "id": 1132562, "state_history_id": 1336910, "tick": 2096, "time": "2026-07-16T10:28:24.537000"}
-- row: {"action_history_id": 600183, "action_status": "SCHEDULED", "id": 1132561, "state_history_id": 1336909, "tick": 2095, "time": "2026-07-16T10:28:23.509000"}
-- RANDOM_ROWS: action_status_history
-- row: {"action_history_id": 556899, "action_status": "SCHEDULED", "id": 990118, "state_history_id": 1222856, "tick": 668, "time": "2026-07-01T15:27:22.953000"}
-- row: {"action_history_id": 567989, "action_status": "EXEC", "id": 1024645, "state_history_id": 1247678, "tick": 56, "time": "2026-07-03T06:43:45.356000"}
-- row: {"action_history_id": 596981, "action_status": "DONE", "id": 1121833, "state_history_id": 1328031, "tick": 291, "time": "2026-07-15T13:18:35.538000"}
-- row: {"action_history_id": 559224, "action_status": "FAILED", "id": 997095, "state_history_id": 1227507, "tick": 1854, "time": "2026-07-01T15:39:18.402000"}
-- row: {"action_history_id": 589918, "action_status": "SCHEDULED", "id": 1097943, "state_history_id": 1308056, "tick": 1741, "time": "2026-07-14T13:09:40.540000"}
-- id: unique identifier, nulls=0, non_nulls=196472, distinct=196472
-- id numeric: min=936092, max=1132563, average=1034327.5000
-- action_history_id: nulls=0, non_nulls=196472, distinct=60074
-- action_history_id numeric: min=540110, max=600183, average=570503.1254
-- tick: nulls=0, non_nulls=196472
-- tick numeric: min=1, max=9220, average=1452.3406
-- time: nulls=0, non_nulls=196472, distinct=196468
-- action_status: nulls=0, non_nulls=196472, distinct=5
-- action_status values: SCHEDULED=120148, DONE=51743, EXEC=16269, FAILED=7865, FAILED_TIMEOUT=447
-- state_history_id: nulls=40828, non_nulls=155644, distinct=155644
-- state_history_id numeric: min=1181268, max=1336911, average=1259089.5000


CREATE TABLE `batch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mlns_id` varchar(255) NOT NULL,
  `create_ts` timestamp NOT NULL,
  `priority` int(11) NOT NULL,
  `finish_ts` timestamp NULL DEFAULT NULL,
  `frozen_ts` timestamp NULL DEFAULT NULL,
  `mlns_port_type` varchar(1) DEFAULT NULL,
  `status` enum('NEW','QUEUED','CANCELLED','FROZEN','EXECUTION','INCOMPLETED','COMPLETED') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mlns_id` (`mlns_id`),
  KEY `batch_create_ts_IDX` (`create_ts`) USING BTREE,
  KEY `batch_create_ts_prio_IDX` (`create_ts`,`priority`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=188
-- LATEST_ROWS: batch
-- row: {"create_ts": "2026-07-02T12:25:10", "finish_ts": "2026-07-02T12:26:31", "frozen_ts": null, "id": 214, "mlns_id": "1", "mlns_port_type": "E", "priority": 7, "status": "COMPLETED"}
-- row: {"create_ts": "2026-07-02T07:04:03", "finish_ts": "2026-07-02T07:38:27", "frozen_ts": null, "id": 213, "mlns_id": "prod-test-3", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-07-01T15:24:48", "finish_ts": "2026-07-01T15:24:48", "frozen_ts": "2026-07-01T15:24:48", "id": 212, "mlns_id": "prod-test-2", "mlns_port_type": "A", "priority": 0, "status": "CANCELLED"}
-- RANDOM_ROWS: batch
-- row: {"create_ts": "2026-02-26T13:40:11", "finish_ts": "2026-02-26T13:40:51", "frozen_ts": null, "id": 148, "mlns_id": "26F1", "mlns_port_type": "A", "priority": 0, "status": "CANCELLED"}
-- row: {"create_ts": "2025-12-10T08:48:38", "finish_ts": "2025-12-10T08:55:41", "frozen_ts": null, "id": 83, "mlns_id": "83", "mlns_port_type": "F", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-18T09:25:11", "finish_ts": "2026-03-18T10:28:34", "frozen_ts": "2026-03-18T09:35:01", "id": 192, "mlns_id": "tbh9006", "mlns_port_type": "A", "priority": 7, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-26T08:51:54", "finish_ts": "2026-03-26T08:55:23", "frozen_ts": null, "id": 207, "mlns_id": "BUNL03", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2025-12-18T12:21:51", "finish_ts": "2025-12-18T12:28:01", "frozen_ts": "2025-12-18T12:22:57", "id": 131, "mlns_id": "115", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- id: unique identifier, nulls=0, non_nulls=188, distinct=188
-- id numeric: min=4, max=214, average=113.7234, median=114.5000
-- mlns_id: unique identifier, nulls=0, non_nulls=188, distinct=188
-- create_ts: nulls=0, non_nulls=188, distinct=187
-- create_ts top_values: 2025-11-24 12:20:27=2, 2025-08-29 12:22:35=1, 2025-10-02 07:39:28=1, 2025-10-02 07:42:47=1, 2025-10-02 07:44:43=1, 2025-10-02 07:46:47=1, 2025-10-02 07:48:17=1, 2025-10-28 08:01:03=1, 2025-11-06 09:48:46=1, 2025-11-06 12:28:47=1
-- priority: nulls=0, non_nulls=188, distinct=7
-- priority numeric: min=0, max=9, average=1.2766, median=0.0000
-- priority values: 0=126, 2=26, 5=14, 7=12, 3=8, 1=1, 9=1
-- finish_ts: nulls=14, non_nulls=174, distinct=163
-- frozen_ts: nulls=113, non_nulls=75, distinct=64
-- mlns_port_type: nulls=0, non_nulls=188, distinct=4
-- mlns_port_type values: A=136, E=35, M=9, F=8
-- status: nulls=0, non_nulls=188, distinct=3
-- status values: COMPLETED=120, CANCELLED=56, INCOMPLETED=12


CREATE TABLE `batch_box_association` (
  `batch_id` int(11) NOT NULL,
  `box_id` int(11) NOT NULL,
  PRIMARY KEY (`batch_id`,`box_id`),
  KEY `box_id` (`box_id`),
  CONSTRAINT `batch_box_association_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`) ON DELETE CASCADE,
  CONSTRAINT `batch_box_association_ibfk_2` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=392
-- LATEST_ROWS: batch_box_association
-- row: {"batch_id": 214, "box_id": 32000246}
-- row: {"batch_id": 213, "box_id": 32001060}
-- row: {"batch_id": 213, "box_id": 32000441}
-- RANDOM_ROWS: batch_box_association
-- row: {"batch_id": 178, "box_id": 17000247}
-- row: {"batch_id": 81, "box_id": 32001078}
-- row: {"batch_id": 77, "box_id": 32001207}
-- row: {"batch_id": 156, "box_id": 32001155}
-- row: {"batch_id": 127, "box_id": 17000217}
-- batch_id: nulls=0, non_nulls=392, distinct=176
-- batch_id numeric: min=5, max=214, average=121.9643, median=137.5000
-- batch_id top_values: 204=22, 143=8, 147=8, 198=8, 141=7, 60=6, 67=6, 73=6, 169=6, 170=6
-- box_id: nulls=0, non_nulls=392, distinct=175
-- box_id numeric: min=17000038, max=32005989, average=27294113.9209, median=32000480.0000
-- box_id top_values: 17000231=17, 17000217=16, 32000019=14, 17000247=13, 32000480=12, 32000121=9, 32001095=7, 32001155=7, 32000057=6, 32001162=6


CREATE TABLE `batch_port` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `port_short_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `batch_port_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=23
-- ALL_ROWS: batch_port
-- row: {"batch_id": 12, "id": 5, "port_short_id": 1}
-- row: {"batch_id": 12, "id": 6, "port_short_id": 2}
-- row: {"batch_id": 15, "id": 7, "port_short_id": 1}
-- row: {"batch_id": 16, "id": 8, "port_short_id": 2}
-- row: {"batch_id": 17, "id": 9, "port_short_id": 2}
-- row: {"batch_id": 20, "id": 10, "port_short_id": 1}
-- row: {"batch_id": 20, "id": 11, "port_short_id": 2}
-- row: {"batch_id": 27, "id": 12, "port_short_id": 2}
-- row: {"batch_id": 28, "id": 13, "port_short_id": 2}
-- row: {"batch_id": 29, "id": 14, "port_short_id": 1}
-- row: {"batch_id": 30, "id": 15, "port_short_id": 2}
-- row: {"batch_id": 31, "id": 16, "port_short_id": 1}
-- row: {"batch_id": 32, "id": 17, "port_short_id": 1}
-- row: {"batch_id": 72, "id": 18, "port_short_id": 1}
-- row: {"batch_id": 73, "id": 19, "port_short_id": 1}
-- row: {"batch_id": 155, "id": 20, "port_short_id": 4}
-- row: {"batch_id": 156, "id": 21, "port_short_id": 3}
-- row: {"batch_id": 157, "id": 22, "port_short_id": 4}
-- row: {"batch_id": 158, "id": 23, "port_short_id": 2}
-- row: {"batch_id": 159, "id": 24, "port_short_id": 3}
-- row: {"batch_id": 160, "id": 25, "port_short_id": 1}
-- row: {"batch_id": 185, "id": 26, "port_short_id": 3}
-- row: {"batch_id": 214, "id": 27, "port_short_id": 2}


CREATE TABLE `batching_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `optimizer` enum('EMPTY','LEVEL_BASED','RESOURCE_BASED') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: batching_params
-- row: {"id": 2, "optimizer": "EMPTY"}


CREATE TABLE `blocked_area` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL,
  `level` int(11) NOT NULL,
  `robot_id` int(11) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `x_begin_mm` int(11) NOT NULL,
  `x_end_mm` int(11) NOT NULL,
  `y_begin_mm` int(11) NOT NULL,
  `y_end_mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49064 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=4
-- ALL_ROWS: blocked_area
-- row: {"id": 46490, "level": 1, "reason": "MALFUNCTION", "robot_id": 6, "timestamp": "2026-07-13T12:17:34", "x_begin_mm": 1500, "x_end_mm": 1980, "y_begin_mm": 6034, "y_end_mm": 6734}
-- row: {"id": 46491, "level": 1, "reason": "MALFUNCTION", "robot_id": 6, "timestamp": "2026-07-13T12:17:34", "x_begin_mm": 1000, "x_end_mm": 1500, "y_begin_mm": 6034, "y_end_mm": 6734}
-- row: {"id": 49024, "level": 0, "reason": "RECOVERING", "robot_id": 5, "timestamp": "2026-07-16T10:13:11", "x_begin_mm": 15300, "x_end_mm": 15920, "y_begin_mm": 200, "y_end_mm": 900}
-- row: {"id": 49025, "level": 0, "reason": "RECOVERING", "robot_id": 5, "timestamp": "2026-07-16T10:13:11", "x_begin_mm": 14800, "x_end_mm": 15300, "y_begin_mm": 200, "y_end_mm": 900}


CREATE TABLE `box` (
  `id` int(11) NOT NULL,
  `height_mm` int(11) NOT NULL,
  `reserve_id` int(11) DEFAULT NULL,
  `cell_id` int(11) DEFAULT NULL,
  `held_by_robot_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_cell_id` (`cell_id`),
  UNIQUE KEY `unique_held_by_robot_id` (`held_by_robot_id`),
  KEY `ix_box_cell_id` (`cell_id`),
  KEY `ix_box_id` (`id`),
  KEY `ix_box_held_by_robot_id` (`held_by_robot_id`),
  CONSTRAINT `box_ibfk_1` FOREIGN KEY (`cell_id`) REFERENCES `cell` (`id`),
  CONSTRAINT `box_ibfk_2` FOREIGN KEY (`held_by_robot_id`) REFERENCES `robot` (`id`),
  CONSTRAINT `min_box_height` CHECK (`height_mm` > 10),
  CONSTRAINT `off_or_on_rack` CHECK (`held_by_robot_id` is null or `cell_id` is null)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=735
-- LATEST_ROWS: box
-- row: {"cell_id": null, "height_mm": 170, "held_by_robot_id": null, "id": 99999999, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32005990, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32005989, "reserve_id": null}
-- RANDOM_ROWS: box
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32000663, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 170, "held_by_robot_id": null, "id": 17000265, "reserve_id": null}
-- row: {"cell_id": 4302, "height_mm": 325, "held_by_robot_id": null, "id": 32000848, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32001197, "reserve_id": null}
-- row: {"cell_id": 7636, "height_mm": 325, "held_by_robot_id": null, "id": 32000817, "reserve_id": null}
-- id: unique identifier, nulls=0, non_nulls=735, distinct=735
-- id numeric: min=1, max=99999999, average=30204860.3034, median=32000619.0000
-- height_mm: nulls=0, non_nulls=735, distinct=2
-- height_mm numeric: min=170, max=325, average=307.0748, median=325.0000
-- height_mm values: 325=650, 170=85
-- reserve_id: all NULL
-- cell_id: unique identifier, nulls=334, non_nulls=401, distinct=401
-- cell_id numeric: min=452, max=16776, average=6409.2244, median=5634.0000
-- held_by_robot_id: all NULL


CREATE TABLE `box_content` (
  `box_id` int(11) NOT NULL,
  `time` timestamp NOT NULL,
  `units` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `box_id` (`box_id`),
  KEY `ix_box_content_id` (`id`),
  CONSTRAINT `box_content_ibfk_1` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: box_content


CREATE TABLE `box_frequency_group` (
  `box_id` int(11) NOT NULL,
  `frequency_group_id` int(11) NOT NULL,
  PRIMARY KEY (`box_id`),
  KEY `frequency_group_id` (`frequency_group_id`),
  CONSTRAINT `box_frequency_group_ibfk_1` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`),
  CONSTRAINT `box_frequency_group_ibfk_2` FOREIGN KEY (`frequency_group_id`) REFERENCES `frequency_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: box_frequency_group


CREATE TABLE `box_movement_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `box_id` int(11) NOT NULL,
  `movement_time` timestamp NOT NULL,
  `task_id` int(11) DEFAULT NULL,
  `new_cell_id` int(11) DEFAULT NULL,
  `robot_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `box_id` (`box_id`),
  KEY `task_id` (`task_id`),
  KEY `new_cell_id` (`new_cell_id`),
  KEY `ix_box_movement_history_id` (`id`),
  KEY `box_movement_history_movement_time_IDX` (`movement_time`) USING BTREE,
  CONSTRAINT `box_movement_history_ibfk_1` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`),
  CONSTRAINT `box_movement_history_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`),
  CONSTRAINT `box_movement_history_ibfk_3` FOREIGN KEY (`new_cell_id`) REFERENCES `cell` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27377 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=26985
-- LATEST_ROWS: box_movement_history
-- row: {"box_id": 32000259, "id": 27376, "movement_time": "2026-07-16T10:28:33", "new_cell_id": 4162, "robot_id": 7, "task_id": 197253}
-- row: {"box_id": 32000259, "id": 27375, "movement_time": "2026-07-16T10:28:02", "new_cell_id": null, "robot_id": 7, "task_id": 197253}
-- row: {"box_id": 32000549, "id": 27374, "movement_time": "2026-07-16T10:27:28", "new_cell_id": 4304, "robot_id": 7, "task_id": 197258}
-- RANDOM_ROWS: box_movement_history
-- row: {"box_id": 32001025, "id": 24964, "movement_time": "2026-06-17T14:37:11", "new_cell_id": 2774, "robot_id": 7, "task_id": 186281}
-- row: {"box_id": 32005987, "id": 7904, "movement_time": "2025-09-18T06:18:52", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 17000222, "id": 8331, "movement_time": "2025-09-24T12:09:24", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 32000492, "id": 6607, "movement_time": "2025-09-08T14:43:09", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 32000537, "id": 20819, "movement_time": "2026-04-16T08:55:43", "new_cell_id": 445, "robot_id": 5, "task_id": 169791}
-- id: unique identifier, nulls=0, non_nulls=26985, distinct=26985
-- id numeric: min=1, max=27376, average=13863.3139, median=13884.0000
-- box_id: nulls=0, non_nulls=26985, distinct=735
-- box_id numeric: min=1, max=99999999, average=30426452.2139, median=32000767.0000
-- box_id top_values: 32000121=262, 32000078=245, 32001146=231, 32000667=223, 32002118=221, 32001098=198, 32000223=195, 32001143=182, 32001092=180, 32005987=174
-- movement_time: nulls=0, non_nulls=26985, distinct=25916
-- movement_time top_values: 2026-03-03 16:38:51=4, 2026-03-03 16:39:10=4, 2026-03-03 16:39:29=4, 2026-03-03 16:39:48=4, 2026-03-03 16:40:46=4, 2026-03-03 16:41:05=4, 2026-03-03 16:41:24=4, 2026-03-03 16:41:43=4, 2026-03-03 16:42:41=4, 2026-03-03 16:43:00=4
-- task_id: nulls=11072, non_nulls=15913, distinct=12031
-- task_id numeric: min=47443, max=197258, average=145727.4449, median=158360.0000
-- task_id top_values: 170757=35, 190637=19, 191151=19, 183378=16, 184571=13, 183376=12, 182958=10, 187661=10, 187669=10, 188252=10
-- new_cell_id: nulls=7486, non_nulls=19499, distinct=3526
-- new_cell_id numeric: min=298, max=41119, average=12638.4390, median=9947.0000
-- new_cell_id top_values: 10187=805, 10209=552, 40789=426, 41119=271, 10231=203, 10253=105, 1299=102, 1156=80, 1871=71, 455=70
-- robot_id: nulls=12541, non_nulls=14444, distinct=8
-- robot_id numeric: min=1, max=8, average=5.7836, median=6.0000
-- robot_id values: 7=4991, 5=4551, 8=1561, 6=1390, 3=935, 1=509, 4=345, 2=162


CREATE TABLE `box_rfid_check` (
  `box_id` int(11) NOT NULL,
  `on_error` varchar(255) NOT NULL,
  PRIMARY KEY (`box_id`),
  KEY `ix_box_rfid_check_box_id` (`box_id`),
  CONSTRAINT `box_rfid_check_ibfk_1` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=694
-- LATEST_ROWS: box_rfid_check
-- row: {"box_id": 99999999, "on_error": "WARN"}
-- row: {"box_id": 32005990, "on_error": "WARN"}
-- row: {"box_id": 32005989, "on_error": "WARN"}
-- RANDOM_ROWS: box_rfid_check
-- row: {"box_id": 32000652, "on_error": "WARN"}
-- row: {"box_id": 32000216, "on_error": "WARN"}
-- row: {"box_id": 32000802, "on_error": "WARN"}
-- row: {"box_id": 32000491, "on_error": "WARN"}
-- row: {"box_id": 32000301, "on_error": "WARN"}
-- box_id: unique identifier, nulls=0, non_nulls=694, distinct=694
-- box_id numeric: min=1, max=99999999, average=30098767.4899, median=32000626.5000
-- on_error: nulls=0, non_nulls=694, distinct=1
-- on_error values: WARN=694


CREATE TABLE `cell` (
  `id` int(11) NOT NULL,
  `stack_id` int(11) NOT NULL,
  `z` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_xyz` (`stack_id`,`z`),
  KEY `ix_cell_stack_id` (`stack_id`),
  CONSTRAINT `cell_ibfk_1` FOREIGN KEY (`stack_id`) REFERENCES `stack` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=41184
-- LATEST_ROWS: cell
-- row: {"id": 41184, "stack_id": 3744, "z": 10}
-- row: {"id": 41183, "stack_id": 3744, "z": 9}
-- row: {"id": 41182, "stack_id": 3744, "z": 8}
-- RANDOM_ROWS: cell
-- row: {"id": 28445, "stack_id": 2586, "z": 9}
-- row: {"id": 6385, "stack_id": 581, "z": 4}
-- row: {"id": 21166, "stack_id": 1925, "z": 1}
-- row: {"id": 8662, "stack_id": 788, "z": 4}
-- row: {"id": 35373, "stack_id": 3216, "z": 7}
-- id: unique identifier, nulls=0, non_nulls=41184, distinct=41184
-- id numeric: min=1, max=41184, average=20592.5000, median=20592.5000
-- stack_id: nulls=0, non_nulls=41184, distinct=3744
-- stack_id numeric: min=1, max=3744, average=1872.5000, median=1872.5000
-- stack_id top_values: 1=11, 2=11, 3=11, 4=11, 5=11, 6=11, 7=11, 8=11, 9=11, 10=11
-- z: nulls=0, non_nulls=41184, distinct=11
-- z numeric: min=0, max=10, average=5.0000, median=5.0000
-- z values: 0=3744, 1=3744, 2=3744, 3=3744, 4=3744, 5=3744, 6=3744, 7=3744, 8=3744, 9=3744, 10=3744


CREATE TABLE `cell_size_x` (
  `id` int(11) NOT NULL,
  `mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=72
-- LATEST_ROWS: cell_size_x
-- row: {"id": 71, "mm": 140}
-- row: {"id": 70, "mm": 480}
-- row: {"id": 69, "mm": 480}
-- RANDOM_ROWS: cell_size_x
-- row: {"id": 8, "mm": 480}
-- row: {"id": 31, "mm": 140}
-- row: {"id": 20, "mm": 480}
-- row: {"id": 3, "mm": 480}
-- row: {"id": 38, "mm": 480}
-- id: unique identifier, nulls=0, non_nulls=72, distinct=72
-- id numeric: min=0, max=71, average=35.5000, median=35.5000
-- mm: nulls=0, non_nulls=72, distinct=3
-- mm numeric: min=140, max=520, average=414.4444, median=480.0000
-- mm values: 480=57, 140=14, 520=1


CREATE TABLE `cell_size_y` (
  `id` int(11) NOT NULL,
  `mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=13
-- ALL_ROWS: cell_size_y
-- row: {"id": 0, "mm": 200}
-- row: {"id": 1, "mm": 680}
-- row: {"id": 2, "mm": 680}
-- row: {"id": 3, "mm": 680}
-- row: {"id": 4, "mm": 197}
-- row: {"id": 5, "mm": 680}
-- row: {"id": 6, "mm": 680}
-- row: {"id": 7, "mm": 680}
-- row: {"id": 8, "mm": 197}
-- row: {"id": 9, "mm": 680}
-- row: {"id": 10, "mm": 680}
-- row: {"id": 11, "mm": 680}
-- row: {"id": 12, "mm": 200}


CREATE TABLE `charging_station` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `head` enum('ZERO','S','E','W','N','TURN','CLBR','BRK') NOT NULL,
  `level` int(11) NOT NULL,
  `charging_speed_prc_by_sec` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `station_unique_position` (`x`,`y`,`level`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=4
-- ALL_ROWS: charging_station
-- row: {"charging_speed_prc_by_sec": 0.033, "head": "E", "id": 1, "level": 0, "x": 0, "y": 9}
-- row: {"charging_speed_prc_by_sec": 0.033, "head": "E", "id": 2, "level": 2, "x": 0, "y": 9}
-- row: {"charging_speed_prc_by_sec": 0.033, "head": "E", "id": 3, "level": 1, "x": 0, "y": 3}
-- row: {"charging_speed_prc_by_sec": 0.033, "head": "E", "id": 4, "level": 3, "x": 0, "y": 3}


CREATE TABLE `cmd_constraint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `head` enum('ZERO','S','E','W','N','TURN','CLBR','BRK') DEFAULT NULL,
  `wheel` enum('ZERO','X','Y','RUN','CLBR','BRK') DEFAULT NULL,
  `command` varchar(30) DEFAULT NULL,
  `param1` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=24
-- ALL_ROWS: cmd_constraint
-- row: {"command": null, "head": "N", "id": 1, "level": 0, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "S", "id": 2, "level": 0, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": null, "id": 3, "level": 0, "param1": null, "wheel": "Y", "x": 0, "y": 9}
-- row: {"command": null, "head": null, "id": 4, "level": 0, "param1": null, "wheel": "Y", "x": 1, "y": 9}
-- row: {"command": null, "head": null, "id": 5, "level": 1, "param1": null, "wheel": "Y", "x": 0, "y": 3}
-- row: {"command": null, "head": null, "id": 7, "level": 2, "param1": null, "wheel": "Y", "x": 0, "y": 9}
-- row: {"command": null, "head": null, "id": 8, "level": 2, "param1": null, "wheel": "Y", "x": 1, "y": 9}
-- row: {"command": null, "head": null, "id": 9, "level": 3, "param1": null, "wheel": "Y", "x": 0, "y": 3}
-- row: {"command": null, "head": null, "id": 10, "level": 3, "param1": null, "wheel": "Y", "x": 1, "y": 3}
-- row: {"command": "ROTATE_WHEELS", "head": null, "id": 11, "level": 0, "param1": null, "wheel": null, "x": 0, "y": 9}
-- row: {"command": "ROTATE_WHEELS", "head": null, "id": 13, "level": 1, "param1": null, "wheel": null, "x": 0, "y": 3}
-- row: {"command": "ROTATE_WHEELS", "head": null, "id": 15, "level": 2, "param1": null, "wheel": null, "x": 0, "y": 9}
-- row: {"command": "ROTATE_WHEELS", "head": null, "id": 17, "level": 3, "param1": null, "wheel": null, "x": 0, "y": 3}
-- row: {"command": null, "head": null, "id": 19, "level": 1, "param1": null, "wheel": null, "x": 1, "y": 3}
-- row: {"command": null, "head": null, "id": 21, "level": 2, "param1": null, "wheel": null, "x": 1, "y": 9}
-- row: {"command": null, "head": null, "id": 22, "level": 3, "param1": null, "wheel": null, "x": 1, "y": 3}
-- row: {"command": null, "head": null, "id": 31, "level": 0, "param1": null, "wheel": null, "x": 1, "y": 9}
-- row: {"command": null, "head": "N", "id": 32, "level": 1, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "S", "id": 33, "level": 1, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "N", "id": 34, "level": 2, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "S", "id": 35, "level": 2, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "N", "id": 36, "level": 3, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": null, "head": "S", "id": 37, "level": 3, "param1": null, "wheel": null, "x": null, "y": null}
-- row: {"command": "ROTATE_HEAD", "head": null, "id": 38, "level": null, "param1": null, "wheel": null, "x": null, "y": null}


CREATE TABLE `column_constraint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `column_unique_position` (`x`,`y`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=42
-- ALL_ROWS: column_constraint
-- row: {"id": 1, "x": 6, "y": 4}
-- row: {"id": 2, "x": 6, "y": 8}
-- row: {"id": 3, "x": 6, "y": 12}
-- row: {"id": 4, "x": 11, "y": 4}
-- row: {"id": 5, "x": 11, "y": 8}
-- row: {"id": 6, "x": 11, "y": 12}
-- row: {"id": 7, "x": 16, "y": 4}
-- row: {"id": 8, "x": 16, "y": 8}
-- row: {"id": 9, "x": 16, "y": 12}
-- row: {"id": 10, "x": 21, "y": 4}
-- row: {"id": 11, "x": 21, "y": 8}
-- row: {"id": 12, "x": 21, "y": 12}
-- row: {"id": 13, "x": 26, "y": 4}
-- row: {"id": 14, "x": 26, "y": 8}
-- row: {"id": 15, "x": 26, "y": 12}
-- row: {"id": 16, "x": 31, "y": 4}
-- row: {"id": 17, "x": 31, "y": 8}
-- row: {"id": 18, "x": 31, "y": 12}
-- row: {"id": 19, "x": 36, "y": 4}
-- row: {"id": 20, "x": 36, "y": 8}
-- row: {"id": 21, "x": 36, "y": 12}
-- row: {"id": 22, "x": 41, "y": 4}
-- row: {"id": 23, "x": 41, "y": 8}
-- row: {"id": 24, "x": 41, "y": 12}
-- row: {"id": 25, "x": 46, "y": 4}
-- row: {"id": 26, "x": 46, "y": 8}
-- row: {"id": 27, "x": 46, "y": 12}
-- row: {"id": 28, "x": 51, "y": 4}
-- row: {"id": 29, "x": 51, "y": 8}
-- row: {"id": 30, "x": 51, "y": 12}
-- row: {"id": 31, "x": 56, "y": 4}
-- row: {"id": 32, "x": 56, "y": 8}
-- row: {"id": 33, "x": 56, "y": 12}
-- row: {"id": 34, "x": 61, "y": 4}
-- row: {"id": 35, "x": 61, "y": 8}
-- row: {"id": 36, "x": 61, "y": 12}
-- row: {"id": 37, "x": 66, "y": 4}
-- row: {"id": 38, "x": 66, "y": 8}
-- row: {"id": 39, "x": 66, "y": 12}
-- row: {"id": 40, "x": 71, "y": 4}
-- row: {"id": 41, "x": 71, "y": 8}
-- row: {"id": 42, "x": 71, "y": 12}


CREATE TABLE `communicator_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mfc_port` int(11) NOT NULL,
  `recv_ports_port` int(11) NOT NULL,
  `recv_n_con_timeout_s` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: communicator_params
-- row: {"id": 1, "mfc_port": 4001, "recv_n_con_timeout_s": 5.0, "recv_ports_port": 4000}


CREATE TABLE `controller_emulator_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `discharge_prc_per_second` float NOT NULL,
  `break_robots` tinyint(1) NOT NULL,
  `robot_break_period_s` float NOT NULL,
  `error_on_robots` tinyint(1) NOT NULL,
  `robot_error_period_s` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: controller_emulator_params
-- row: {"break_robots": 0, "discharge_prc_per_second": 0.014, "error_on_robots": 0, "id": 1, "robot_break_period_s": 55.0, "robot_error_period_s": 55.0}


CREATE TABLE `dismissed_notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `notification_key` varchar(255) NOT NULL,
  `dismissed_at` timestamp NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dismissed_user_key` (`user_id`,`notification_key`),
  KEY `ix_dismissed_notifications_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=5
-- ALL_ROWS: dismissed_notifications
-- row: {"dismissed_at": "2026-07-14T14:46:16", "id": 1, "notification_key": "fa:2026-07-14T15:08:33.183000:7:TAKE_BOX", "user_id": 12}
-- row: {"dismissed_at": "2026-07-14T14:46:17", "id": 2, "notification_key": "fa:2026-07-14T15:08:16.202000:7:MOVE", "user_id": 12}
-- row: {"dismissed_at": "2026-07-14T14:46:20", "id": 3, "notification_key": "fa:2026-07-14T15:07:19.548000:7:MOVE", "user_id": 12}
-- row: {"dismissed_at": "2026-07-15T08:35:23", "id": 4, "notification_key": "ee:2026-07-15T09:29:32.120227Z:FULL_NO_DB_HELD: robot 5, DB box None, RFID None.", "user_id": 12}
-- row: {"dismissed_at": "2026-07-15T11:59:24", "id": 5, "notification_key": "ee:2026-07-15T12:53:54.568197Z:FULL_NO_DB_HELD: robot 5, DB box None, RFID None.", "user_id": 12}


CREATE TABLE `drive_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x_min` int(11) NOT NULL,
  `x_max` int(11) NOT NULL,
  `y_min` int(11) NOT NULL,
  `y_max` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: drive_params
-- row: {"id": 1, "x_max": 70, "x_min": 0, "y_max": 11, "y_min": 1}


CREATE TABLE `executor_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_timeout_tolerance_s` float NOT NULL,
  `restart_delay_s` float NOT NULL,
  `fail_and_timeout_minutes` int(11) NOT NULL,
  `fail_and_timeout_n_in_minutes` int(11) NOT NULL,
  `stop_timeout_tolerance_s` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: executor_params
-- row: {"action_timeout_tolerance_s": 7.7, "fail_and_timeout_minutes": 10, "fail_and_timeout_n_in_minutes": 40, "id": 4, "restart_delay_s": 1.0, "stop_timeout_tolerance_s": 20}


CREATE TABLE `frequency_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `order_share_pct` float NOT NULL,
  `box_share_pct` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: frequency_group


CREATE TABLE `grid_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `levels` int(11) NOT NULL,
  `x_min` int(11) NOT NULL,
  `x_max` int(11) NOT NULL,
  `y_min` int(11) NOT NULL,
  `y_max` int(11) NOT NULL,
  `max_depth` int(11) NOT NULL,
  `belt_length_mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: grid_params
-- row: {"belt_length_mm": 5500, "id": 1, "levels": 4, "max_depth": 11, "x_max": 71, "x_min": 0, "y_max": 12, "y_min": 0}


CREATE TABLE `levels` (
  `level_height_mm` int(11) NOT NULL,
  `max_stack_height_mm` int(11) NOT NULL,
  `lift_to_stack_bottom_mm` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=4
-- ALL_ROWS: levels
-- row: {"id": 0, "level_height_mm": 2488, "lift_to_stack_bottom_mm": 2400, "max_stack_height_mm": 1556}
-- row: {"id": 1, "level_height_mm": 2388, "lift_to_stack_bottom_mm": 1691, "max_stack_height_mm": 1247}
-- row: {"id": 2, "level_height_mm": 2088, "lift_to_stack_bottom_mm": 1691, "max_stack_height_mm": 1247}
-- row: {"id": 3, "level_height_mm": 2160, "lift_to_stack_bottom_mm": 1250, "max_stack_height_mm": 806}


CREATE TABLE `lift_correction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `robot_id` int(11) NOT NULL,
  `mfc_height_mm` int(11) NOT NULL,
  `encoder_height_mm` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=7
-- ALL_ROWS: lift_correction
-- row: {"encoder_height_mm": 1800, "id": 6, "mfc_height_mm": 1800, "robot_id": 1}
-- row: {"encoder_height_mm": 2300, "id": 7, "mfc_height_mm": 2362, "robot_id": 1}
-- row: {"encoder_height_mm": 742, "id": 8, "mfc_height_mm": 785, "robot_id": 5}
-- row: {"encoder_height_mm": 2185, "id": 9, "mfc_height_mm": 2025, "robot_id": 5}
-- row: {"encoder_height_mm": 657, "id": 12, "mfc_height_mm": 785, "robot_id": 7}
-- row: {"encoder_height_mm": 1930, "id": 13, "mfc_height_mm": 2025, "robot_id": 7}
-- row: {"encoder_height_mm": 1, "id": 14, "mfc_height_mm": 1, "robot_id": 7}


CREATE TABLE `lift_timings` (
  `dlift_mm` int(11) NOT NULL,
  `is_with_box` tinyint(1) NOT NULL,
  `time_s` float NOT NULL,
  PRIMARY KEY (`dlift_mm`,`is_with_box`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=10
-- ALL_ROWS: lift_timings
-- row: {"dlift_mm": -2025, "is_with_box": 0, "time_s": 6.0}
-- row: {"dlift_mm": -2018, "is_with_box": 1, "time_s": 8.5}
-- row: {"dlift_mm": -800, "is_with_box": 1, "time_s": 7.0}
-- row: {"dlift_mm": -795, "is_with_box": 0, "time_s": 3.5}
-- row: {"dlift_mm": 0, "is_with_box": 0, "time_s": 0.5}
-- row: {"dlift_mm": 0, "is_with_box": 1, "time_s": 1.0}
-- row: {"dlift_mm": 795, "is_with_box": 0, "time_s": 6.5}
-- row: {"dlift_mm": 800, "is_with_box": 1, "time_s": 6.5}
-- row: {"dlift_mm": 1600, "is_with_box": 1, "time_s": 9.5}
-- row: {"dlift_mm": 2025, "is_with_box": 0, "time_s": 8.0}


CREATE TABLE `move_robot` (
  `id` int(11) NOT NULL,
  `robot_id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `head` enum('ZERO','S','E','W','N','TURN','CLBR','BRK') DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `move_robot_ibfk_1` FOREIGN KEY (`id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=18119
-- LATEST_ROWS: move_robot
-- row: {"head": null, "id": 192722, "robot_id": 7, "x": 8, "y": 1}
-- row: {"head": null, "id": 192719, "robot_id": 7, "x": 2, "y": 1}
-- row: {"head": null, "id": 192718, "robot_id": 5, "x": 2, "y": 3}
-- RANDOM_ROWS: move_robot
-- row: {"head": null, "id": 19943, "robot_id": 1, "x": 0, "y": 9}
-- row: {"head": null, "id": 7890, "robot_id": 6, "x": 57, "y": 9}
-- row: {"head": null, "id": 145836, "robot_id": 1, "x": 9, "y": 5}
-- row: {"head": null, "id": 121358, "robot_id": 5, "x": 30, "y": 9}
-- row: {"head": null, "id": 73390, "robot_id": 5, "x": 9, "y": 9}
-- id: unique identifier, nulls=0, non_nulls=18119, distinct=18119
-- id numeric: min=3777, max=192722, average=77885.7924, median=111164.0000
-- robot_id: nulls=0, non_nulls=18119, distinct=8
-- robot_id numeric: min=1, max=8, average=4.8725, median=5.0000
-- robot_id values: 5=3900, 3=3390, 7=2961, 8=2243, 6=1745, 4=1709, 1=1704, 2=467
-- x: nulls=0, non_nulls=18119, distinct=65
-- x numeric: min=0, max=70, average=23.7113, median=18.0000
-- y: nulls=0, non_nulls=18119, distinct=11
-- y numeric: min=1, max=11, average=5.7641, median=6.0000
-- y values: 1=2587, 3=2273, 11=2100, 9=2089, 2=2072, 7=1845, 5=1753, 10=1725, 6=1665, 8=7, 4=3
-- head: nulls=18055, non_nulls=64, distinct=5
-- head values: E=23, W=21, ZERO=14, S=3, N=3


CREATE TABLE `move_timings` (
  `dist_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`dist_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=5
-- ALL_ROWS: move_timings
-- row: {"dist_mm": 5, "time_s": 2.0}
-- row: {"dist_mm": 480, "time_s": 6.8}
-- row: {"dist_mm": 680, "time_s": 7.7}
-- row: {"dist_mm": 2237, "time_s": 9.5}
-- row: {"dist_mm": 19540, "time_s": 24.7}


CREATE TABLE `nogo_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `level` int(11) NOT NULL,
  `x_begin` int(11) NOT NULL,
  `x_end` int(11) NOT NULL,
  `y_begin` int(11) NOT NULL,
  `y_end` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=23
-- ALL_ROWS: nogo_zone
-- row: {"id": 102, "level": 0, "x_begin": 0, "x_end": 71, "y_begin": 0, "y_end": 0}
-- row: {"id": 103, "level": 0, "x_begin": 0, "x_end": 71, "y_begin": 12, "y_end": 12}
-- row: {"id": 104, "level": 0, "x_begin": 71, "x_end": 71, "y_begin": 0, "y_end": 12}
-- row: {"id": 105, "level": 1, "x_begin": 0, "x_end": 71, "y_begin": 0, "y_end": 0}
-- row: {"id": 106, "level": 1, "x_begin": 0, "x_end": 71, "y_begin": 12, "y_end": 12}
-- row: {"id": 107, "level": 1, "x_begin": 71, "x_end": 71, "y_begin": 0, "y_end": 12}
-- row: {"id": 108, "level": 2, "x_begin": 0, "x_end": 71, "y_begin": 0, "y_end": 0}
-- row: {"id": 109, "level": 2, "x_begin": 0, "x_end": 71, "y_begin": 12, "y_end": 12}
-- row: {"id": 110, "level": 2, "x_begin": 71, "x_end": 71, "y_begin": 0, "y_end": 12}
-- row: {"id": 111, "level": 3, "x_begin": 0, "x_end": 71, "y_begin": 0, "y_end": 0}
-- row: {"id": 112, "level": 3, "x_begin": 0, "x_end": 71, "y_begin": 12, "y_end": 12}
-- row: {"id": 113, "level": 3, "x_begin": 71, "x_end": 71, "y_begin": 0, "y_end": 12}
-- row: {"id": 114, "level": 0, "x_begin": 0, "x_end": 1, "y_begin": 0, "y_end": 8}
-- row: {"id": 115, "level": 0, "x_begin": 0, "x_end": 1, "y_begin": 10, "y_end": 12}
-- row: {"id": 116, "level": 1, "x_begin": 0, "x_end": 1, "y_begin": 0, "y_end": 2}
-- row: {"id": 117, "level": 1, "x_begin": 0, "x_end": 1, "y_begin": 4, "y_end": 12}
-- row: {"id": 118, "level": 2, "x_begin": 0, "x_end": 1, "y_begin": 0, "y_end": 8}
-- row: {"id": 119, "level": 2, "x_begin": 0, "x_end": 1, "y_begin": 10, "y_end": 12}
-- row: {"id": 120, "level": 3, "x_begin": 0, "x_end": 1, "y_begin": 0, "y_end": 2}
-- row: {"id": 121, "level": 3, "x_begin": 0, "x_end": 1, "y_begin": 4, "y_end": 12}
-- row: {"id": 122, "level": 0, "x_begin": 70, "x_end": 70, "y_begin": 1, "y_end": 2}
-- row: {"id": 123, "level": 0, "x_begin": 70, "x_end": 70, "y_begin": 6, "y_end": 6}
-- row: {"id": 124, "level": 0, "x_begin": 70, "x_end": 70, "y_begin": 10, "y_end": 11}


CREATE TABLE `obstacle_constraint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `type` varchar(30) NOT NULL,
  `level` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `obstacle_unique_position` (`x`,`y`,`level`)
) ENGINE=InnoDB AUTO_INCREMENT=687 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=682
-- LATEST_ROWS: obstacle_constraint
-- row: {"id": 682, "level": 3, "type": "CELL_INTERIOR", "x": 1, "y": 11}
-- row: {"id": 681, "level": 1, "type": "CELL_INTERIOR", "x": 1, "y": 11}
-- row: {"id": 680, "level": 3, "type": "CELL_INTERIOR", "x": 0, "y": 11}
-- RANDOM_ROWS: obstacle_constraint
-- row: {"id": 510, "level": 3, "type": "CELL_INTERIOR", "x": 48, "y": 12}
-- row: {"id": 207, "level": 0, "type": "CELL_INTERIOR", "x": 45, "y": 0}
-- row: {"id": 230, "level": 3, "type": "CELL_INTERIOR", "x": 50, "y": 0}
-- row: {"id": 145, "level": 2, "type": "CELL_INTERIOR", "x": 29, "y": 0}
-- row: {"id": 155, "level": 0, "type": "CELL_INTERIOR", "x": 32, "y": 0}
-- id: unique identifier, nulls=0, non_nulls=682, distinct=682
-- id numeric: min=1, max=682, average=341.5000, median=341.5000
-- x: nulls=0, non_nulls=682, distinct=72
-- x numeric: min=0, max=71, average=32.7478, median=32.0000
-- x top_values: 0=48, 1=48, 71=34, 2=8, 3=8, 4=8, 5=8, 6=8, 7=8, 8=8
-- y: nulls=0, non_nulls=682, distinct=13
-- y numeric: min=0, max=12, average=6.0000, median=6.0000
-- y values: 0=288, 12=288, 2=12, 6=12, 10=12, 4=10, 5=10, 7=10, 8=10, 1=9, 11=9, 3=6, 9=6
-- type: nulls=0, non_nulls=682, distinct=1
-- type values: CELL_INTERIOR=682
-- level: nulls=0, non_nulls=682, distinct=4
-- level numeric: min=0, max=3, average=1.5132, median=2.0000
-- level values: 2=173, 3=173, 0=169, 1=167


CREATE TABLE `planner_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `battery_min_charge` int(11) NOT NULL,
  `battery_low_charge` int(11) NOT NULL,
  `battery_medium_charge` int(11) NOT NULL,
  `max_wait_at_picking_port_s` float NOT NULL,
  `wait_at_picking_port_storage_task_s` float NOT NULL,
  `n_robots_tried_for_task` int(11) NOT NULL,
  `n_positions_tried_at_box` int(11) NOT NULL,
  `mapf_n_of_robot_planning_orders_tried_per_path` int(11) NOT NULL,
  `a_star_max_n_actions_per_path` int(11) NOT NULL,
  `a_star_max_forward_plan_time_s` float NOT NULL,
  `port_lift_up_delta_mm` int(11) NOT NULL,
  `battery_full_charge` int(11) DEFAULT 85,
  `max_gripper_inclination` float NOT NULL DEFAULT 2,
  `try_restacking` tinyint(1) NOT NULL DEFAULT 0,
  `steer_at_least_once_before_lift` tinyint(1) NOT NULL DEFAULT 0,
  `guarantee_steering_y_before_lift` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: planner_params
-- row: {"a_star_max_forward_plan_time_s": 180.0, "a_star_max_n_actions_per_path": 750, "battery_full_charge": 85, "battery_low_charge": 25, "battery_medium_charge": 35, "battery_min_charge": 10, "guarantee_steering_y_before_lift": 0, "id": 4, "mapf_n_of_robot_planning_orders_tried_per_path": 6, "max_gripper_inclination": 5.0, "max_wait_at_picking_port_s": 15.0, "n_positions_tried_at_box": 4, "n_robots_tried_for_task": 1, "port_lift_up_delta_mm": 400, "steer_at_least_once_before_lift": 0, "try_restacking": 1, "wait_at_picking_port_storage_task_s": 5.0}


CREATE TABLE `port_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `top_position_sensor_value` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: port_params
-- row: {"id": 1, "top_position_sensor_value": 1600}


CREATE TABLE `put_box_timings` (
  `lift_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`lift_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=5
-- ALL_ROWS: put_box_timings
-- row: {"lift_mm": 1, "time_s": 1.0}
-- row: {"lift_mm": 450, "time_s": 7.0}
-- row: {"lift_mm": 786, "time_s": 13.0}
-- row: {"lift_mm": 1500, "time_s": 19.0}
-- row: {"lift_mm": 4500, "time_s": 37.0}


CREATE TABLE `robot` (
  `id` int(11) NOT NULL,
  `port` int(11) NOT NULL,
  `ip` varchar(32) NOT NULL,
  `level` int(11) NOT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=8
-- ALL_ROWS: robot
-- row: {"id": 1, "ip": "192.168.127.71", "level": 2, "port": 2000, "status": "OUT_OF_GRID"}
-- row: {"id": 2, "ip": "192.168.127.74", "level": 3, "port": 2000, "status": "OUT_OF_GRID"}
-- row: {"id": 3, "ip": "192.168.127.77", "level": 3, "port": 2000, "status": "OUT_OF_GRID"}
-- row: {"id": 4, "ip": "192.168.127.80", "level": 2, "port": 2000, "status": "OUT_OF_GRID"}
-- row: {"id": 5, "ip": "192.168.127.83", "level": 0, "port": 2000, "status": "NOT_IN_USE"}
-- row: {"id": 6, "ip": "192.168.127.86", "level": 1, "port": 2000, "status": "MALFUNCTION"}
-- row: {"id": 7, "ip": "192.168.127.89", "level": 0, "port": 2000, "status": "PLANNABLE"}
-- row: {"id": 8, "ip": "192.168.127.92", "level": 1, "port": 2000, "status": "OUT_OF_GRID"}


CREATE TABLE `robot_dimensions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rail_width_mm` int(11) NOT NULL,
  `body_case_x_width_mm` int(11) NOT NULL,
  `body_case_y_width_mm` int(11) NOT NULL,
  `sweeping_head_diameter_mm` int(11) NOT NULL,
  `sweeping_body_diameter_mm` int(11) NOT NULL,
  `south_north_gripper_retract_at_port_mm` int(11) NOT NULL,
  `gripper_full_extension_mm` int(11) NOT NULL,
  `lift_tolerance` int(11) NOT NULL,
  `gripper_tolerance_mm` int(11) NOT NULL,
  `small_head` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: robot_dimensions
-- row: {"body_case_x_width_mm": 500, "body_case_y_width_mm": 700, "gripper_full_extension_mm": 200, "gripper_tolerance_mm": 10, "id": 1, "lift_tolerance": 45, "rail_width_mm": 20, "small_head": 0, "south_north_gripper_retract_at_port_mm": 130, "sweeping_body_diameter_mm": 880, "sweeping_head_diameter_mm": 1980}


CREATE TABLE `robot_state_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `robot_id` int(11) NOT NULL,
  `timestamp` timestamp(3) NOT NULL,
  `ready_for_next_command` enum('N_CON','N_RDY','READY','EXEC','ALARM') DEFAULT NULL,
  `battery_charge` int(11) NOT NULL,
  `lift_state` enum('ZERO','TOP','MID','RUN','CLBR','BRK') NOT NULL,
  `lift_mm` int(11) NOT NULL,
  `gripper_state` enum('ZERO','FULL','EMPT','UNCL','RUN','CLBR','BRK') NOT NULL,
  `wheels_direction` enum('ZERO','X','Y','RUN','CLBR','BRK') NOT NULL,
  `wheel_drives` enum('STOP','RUN','CLBR','BRK','WELL','ROUGH','LOST') DEFAULT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `head_state` enum('ZERO','S','E','W','N','TURN','CLBR','BRK') NOT NULL,
  `gripper_extension_state` enum('ZERO','RETR','EXTN','MID','RUN','CLBR','BRK') NOT NULL,
  `head_rotation_deg` int(11) NOT NULL,
  `gripper_extension_mm` int(11) NOT NULL,
  `error_id0` int(11) NOT NULL,
  `error_id1` int(11) NOT NULL,
  `error_id2` int(11) NOT NULL,
  `error_id3` int(11) NOT NULL,
  `error_id4` int(11) NOT NULL,
  `error_id5` int(11) NOT NULL,
  `error_id6` int(11) NOT NULL,
  `error_id7` int(11) NOT NULL,
  `error_id8` int(11) NOT NULL,
  `error_id9` int(11) NOT NULL,
  `speed` int(11) NOT NULL,
  `acceleration` int(11) NOT NULL,
  `box_id` int(11) DEFAULT NULL,
  `encoder_wheel_1` double DEFAULT 0,
  `encoder_wheel_2` double DEFAULT 0,
  `encoder_wheel_3` double DEFAULT 0,
  `encoder_wheel_4` double DEFAULT 0,
  `pos_sensors` int(11) DEFAULT 0,
  `gripper_acc_x` int(11) DEFAULT 0,
  `gripper_acc_y` int(11) DEFAULT 0,
  `gripper_sensors` int(11) DEFAULT 0,
  `x_mm` int(11) DEFAULT 0,
  `y_mm` int(11) DEFAULT 0,
  `steering_encoder_deg` float DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `robot_state_history_timestamp_IDX` (`timestamp`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1336912 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=155644
-- LATEST_ROWS: robot_state_history
-- row: {"acceleration": 0, "battery_charge": 41, "box_id": null, "encoder_wheel_1": "4618.1020000000", "encoder_wheel_2": "4616.7850000000", "encoder_wheel_3": "-4628.2440000000", "encoder_wheel_4": "-4740.0040000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1336911, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.806, "timestamp": "2026-07-16T10:28:33.625000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 28, "x_mm": 11780, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 41, "box_id": null, "encoder_wheel_1": "4618.0960000000", "encoder_wheel_2": "4616.7780000000", "encoder_wheel_3": "-4628.2390000000", "encoder_wheel_4": "-4740.0020000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": 1, "head_state": "E", "id": 1336910, "level": 0, "lift_mm": 61, "lift_state": "MID", "pos_sensors": 31, "ready_for_next_command": "EXEC", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.806, "timestamp": "2026-07-16T10:28:24.428000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 28, "x_mm": 11780, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 41, "box_id": 32000259, "encoder_wheel_1": "4618.0960000000", "encoder_wheel_2": "4616.7770000000", "encoder_wheel_3": "-4628.2400000000", "encoder_wheel_4": "-4740.0040000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": 1, "head_state": "E", "id": 1336909, "level": 0, "lift_mm": 6, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.806, "timestamp": "2026-07-16T10:28:23.465000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 28, "x_mm": 11780, "y": 1, "y_mm": 200}
-- RANDOM_ROWS: robot_state_history
-- row: {"acceleration": 0, "battery_charge": 83, "box_id": 32001060, "encoder_wheel_1": "15432.4020000000", "encoder_wheel_2": "6527.1780000000", "encoder_wheel_3": "-6515.9100000000", "encoder_wheel_4": "-15762.5570000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": 1, "head_state": "E", "id": 1232522, "level": 0, "lift_mm": 6, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.709, "timestamp": "2026-07-02T07:14:53.371000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 28, "x_mm": 11780, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 58, "box_id": null, "encoder_wheel_1": "16214.1040000000", "encoder_wheel_2": "13639.5450000000", "encoder_wheel_3": "-13504.5240000000", "encoder_wheel_4": "-16229.3280000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1317233, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 5, "speed": 0, "steering_encoder_deg": 91.851, "timestamp": "2026-07-15T08:53:47.020000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 38, "x_mm": 15900, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 86, "box_id": 32000262, "encoder_wheel_1": "-6835.5130000000", "encoder_wheel_2": "-5467.2570000000", "encoder_wheel_3": "5472.9120000000", "encoder_wheel_4": "6839.4550000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1201312, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "EXEC", "robot_id": 5, "speed": 0, "steering_encoder_deg": 0.127, "timestamp": "2026-06-30T05:37:25.078000", "wheel_drives": "WELL", "wheels_direction": "Y", "x": 2, "x_mm": 1000, "y": 2, "y_mm": 880}
-- row: {"acceleration": 0, "battery_charge": 57, "box_id": 32000601, "encoder_wheel_1": "316.5680000000", "encoder_wheel_2": "1650.9230000000", "encoder_wheel_3": "-1653.1740000000", "encoder_wheel_4": "-302.2640000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": 1, "head_state": "E", "id": 1203894, "level": 0, "lift_mm": 7, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 0.295, "timestamp": "2026-06-30T05:57:07.726000", "wheel_drives": "WELL", "wheels_direction": "Y", "x": 9, "x_mm": 4020, "y": 2, "y_mm": 880}
-- row: {"acceleration": 0, "battery_charge": 92, "box_id": 32000590, "encoder_wheel_1": "2146.8000000000", "encoder_wheel_2": "3888.4860000000", "encoder_wheel_3": "-3897.7930000000", "encoder_wheel_4": "-2153.2640000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -1, "gripper_acc_y": -1, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1196085, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 0.297, "timestamp": "2026-06-29T13:37:04.441000", "wheel_drives": "WELL", "wheels_direction": "Y", "x": 9, "x_mm": 4020, "y": 9, "y_mm": 4674}
-- id: unique identifier, nulls=0, non_nulls=155644, distinct=155644
-- id numeric: min=1181268, max=1336911, average=1259089.5000
-- robot_id: nulls=0, non_nulls=155644
-- robot_id numeric: min=5, max=7, average=6.0969
-- timestamp: nulls=0, non_nulls=155644, distinct=70052
-- ready_for_next_command: nulls=0, non_nulls=155644
-- battery_charge: nulls=0, non_nulls=155644
-- battery_charge numeric: min=0, max=99, average=68.6860
-- lift_state: nulls=0, non_nulls=155644
-- lift_mm: nulls=0, non_nulls=155644
-- lift_mm numeric: min=0, max=2310, average=41.0692
-- gripper_state: nulls=0, non_nulls=155644
-- wheels_direction: nulls=0, non_nulls=155644
-- wheel_drives: nulls=0, non_nulls=155644
-- x: nulls=0, non_nulls=155644
-- x numeric: min=0, max=70, average=28.5578
-- y: nulls=0, non_nulls=155644
-- y numeric: min=0, max=11, average=3.3814
-- level: nulls=0, non_nulls=155644
-- level numeric: min=0, max=1, average=0.0181
-- head_state: nulls=0, non_nulls=155644
-- gripper_extension_state: nulls=0, non_nulls=155644
-- head_rotation_deg: nulls=0, non_nulls=155644
-- head_rotation_deg numeric: min=-1, max=1, average=0.9549
-- gripper_extension_mm: nulls=0, non_nulls=155644
-- gripper_extension_mm numeric: min=0, max=140, average=1.5381
-- error_id0: nulls=0, non_nulls=155644
-- error_id0 numeric: min=0, max=1, average=0.0001
-- error_id1: nulls=0, non_nulls=155644
-- error_id1 numeric: min=0, max=1001, average=0.1158
-- error_id2: nulls=0, non_nulls=155644
-- error_id2 numeric: min=0, max=1001, average=0.1929
-- error_id3: nulls=0, non_nulls=155644
-- error_id3 numeric: min=0, max=1008, average=3.3987
-- error_id4: nulls=0, non_nulls=155644
-- error_id4 numeric: min=0, max=1015, average=46.7297
-- error_id5: nulls=0, non_nulls=155644
-- error_id5 numeric: min=0, max=27, average=0.0038
-- error_id6: nulls=0, non_nulls=155644
-- error_id6 numeric: min=0, max=3, average=0.0001
-- error_id7: nulls=0, non_nulls=155644
-- error_id7 numeric: min=0, max=0, average=0.0000
-- error_id8: nulls=0, non_nulls=155644
-- error_id8 numeric: min=0, max=0, average=0.0000
-- error_id9: nulls=0, non_nulls=155644
-- error_id9 numeric: min=0, max=10215, average=57.8514
-- speed: nulls=0, non_nulls=155644
-- speed numeric: min=-254, max=322, average=-0.0416
-- acceleration: nulls=0, non_nulls=155644
-- acceleration numeric: min=-552, max=600, average=-0.0476
-- box_id: nulls=70024, non_nulls=85620
-- box_id numeric: min=32000230, max=32002114, average=32000614.0753
-- encoder_wheel_1: nulls=0, non_nulls=155644
-- encoder_wheel_1 numeric: min=-22644.1570000000, max=8598220.5390000008, average=8796.59
-- encoder_wheel_2: nulls=0, non_nulls=155644
-- encoder_wheel_2 numeric: min=-26318.9080000000, max=85110.8180000000, average=8640.19
-- encoder_wheel_3: nulls=0, non_nulls=155644
-- encoder_wheel_3 numeric: min=-33647.5540000000, max=102446.1750000000, average=-8603.04
-- encoder_wheel_4: nulls=0, non_nulls=155644
-- encoder_wheel_4 numeric: min=-32266.6720000000, max=35083.3930000000, average=-8191.91
-- pos_sensors: nulls=0, non_nulls=155644
-- pos_sensors numeric: min=0, max=31, average=29.0836
-- gripper_acc_x: nulls=0, non_nulls=155644
-- gripper_acc_x numeric: min=-30, max=67, average=-0.2558
-- gripper_acc_y: nulls=0, non_nulls=155644
-- gripper_acc_y numeric: min=-50, max=42, average=-0.2135
-- gripper_sensors: nulls=0, non_nulls=155644
-- gripper_sensors numeric: min=0, max=21, average=8.3152
-- x_mm: nulls=0, non_nulls=155644
-- x_mm numeric: min=-13887, max=29244, average=12019.3805
-- y_mm: nulls=0, non_nulls=155644
-- y_mm numeric: min=-68765, max=11853, average=1599.6453
-- steering_encoder_deg: nulls=0, non_nulls=155644
-- steering_encoder_deg numeric: min=-0.138, max=91.972, average=51.5589


CREATE TABLE `safety_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `check_name` varchar(64) NOT NULL,
  `message` varchar(512) NOT NULL,
  `tick` int(11) NOT NULL,
  `time` timestamp NOT NULL,
  `robot_id` int(11) NOT NULL,
  `task_id` int(11) DEFAULT NULL,
  `box_id` int(11) DEFAULT NULL,
  `command_id` varchar(30) NOT NULL,
  `param1` int(11) NOT NULL,
  `start_tick` int(11) NOT NULL,
  `finished_tick` int(11) NOT NULL,
  `json_data` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `safety_events_time_IDX` (`time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=26890 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=9713
-- LATEST_ROWS: safety_events
-- row: {"box_id": 32000549, "check_name": "StartStateCheck", "command_id": "PUT_BOX", "finished_tick": 2003, "id": 26889, "json_data": "{'command_id': 'PUT_BOX', 'param1': 820, 'param2': 0, 'param3': 0, 'param4': 100, 'box_id': 32000549, 'dist_mm': 0, 'start_tick': 1993, 'finished_tick': 2003, 'start_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:26:08.019288Z', 'ready_for_next_command': 2, 'battery_charge': 41, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 12, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000549, 'encoder_wheel_1': 4920.0, 'encoder_wheel_2': 5320.0, 'encoder_wheel_3': -5320.0, 'encoder_wheel_4': -4920.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 7, 'x_mm': 5120, 'y_mm': 200}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:26:08.019288Z', 'ready_for_next_command': 2, 'battery_charge': 41, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 12, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 4920.0, 'encoder_wheel_2': 5320.0, 'encoder_wheel_3': -5320.0, 'encoder_wheel_4': -4920.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 7, 'x_mm': 5120, 'y_mm': 200}, 'expected_duration_s': 6.369839728023312, 'task_id': 197255, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :READY 12 1  0 steer=X head=E(0  ) lift=TOP(    0mm) grip=FULL MID  0   box=32000549 pos=11111 grip=111  41%\nRecvd:7 :EXEC  12 1  0 steer=X head=E(1  ) lift=TOP(    7mm) grip=FULL MID  0   box=32000549 whls=RUN vel=-10 pos=1110 grip=111  41%", "param1": 820, "robot_id": 7, "start_tick": 1993, "task_id": 197255, "tick": 1993, "time": "2026-07-16T10:26:51"}
-- row: {"box_id": 32000259, "check_name": "StartStateCheck", "command_id": "PUT_BOX", "finished_tick": 1923, "id": 26888, "json_data": "{'command_id': 'PUT_BOX', 'param1': 1130, 'param2': 0, 'param3': 0, 'param4': 100, 'box_id': 32000259, 'dist_mm': 0, 'start_tick': 1909, 'finished_tick': 1923, 'start_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:24:13.371171Z', 'ready_for_next_command': 2, 'battery_charge': 41, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 28, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000259, 'encoder_wheel_1': 11580.0, 'encoder_wheel_2': 11980.0, 'encoder_wheel_3': -11980.0, 'encoder_wheel_4': -11580.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 11780, 'y_mm': 200}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:24:13.371171Z', 'ready_for_next_command': 2, 'battery_charge': 41, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 28, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 11580.0, 'encoder_wheel_2': 11980.0, 'encoder_wheel_3': -11980.0, 'encoder_wheel_4': -11580.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 11780, 'y_mm': 200}, 'expected_duration_s': 8.402379796017485, 'task_id': 197253, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :READY 28 1  0 steer=X head=E(0  ) lift=TOP(    0mm) grip=FULL MID  0   box=32000259 pos=11111 grip=1001  41%\nRecvd:7 :ALARM 28 1  0 steer=X head=E(1  ) lift=TOP(    8mm) grip=FULL MID  0   box=32000259 pos=11111 grip=111 errs=(4, 1012) 41%", "param1": 1130, "robot_id": 7, "start_tick": 1909, "task_id": 197253, "tick": 1909, "time": "2026-07-16T10:25:37"}
-- row: {"box_id": 32000873, "check_name": "StartStateCheck", "command_id": "MOVE", "finished_tick": 1263, "id": 26887, "json_data": "{'command_id': 'MOVE', 'param1': -16, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': -6660, 'start_tick': 1241, 'finished_tick': 1263, 'start_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:17:09.566164Z', 'ready_for_next_command': 2, 'battery_charge': 42, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 28, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000873, 'encoder_wheel_1': 11580.0, 'encoder_wheel_2': 11980.0, 'encoder_wheel_3': -11980.0, 'encoder_wheel_4': -11580.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 11780, 'y_mm': 200}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-07-16T11:17:22.951594Z', 'ready_for_next_command': 2, 'battery_charge': 42, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 12, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000873, 'encoder_wheel_1': 4920.0, 'encoder_wheel_2': 5320.0, 'encoder_wheel_3': -5320.0, 'encoder_wheel_4': -4920.0, 'steering_encoder_deg': 89.806, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 5120, 'y_mm': 200}, 'expected_duration_s': 13.385430335998535, 'task_id': 197203, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :READY 28 1  0 steer=X head=E(0  ) lift=TOP(    0mm) grip=FULL MID  0   box=32000873 pos=11111 grip=1001  42%\nRecvd:7 :ALARM 28 1  0 steer=X head=E(1  ) lift=TOP(    7mm) grip=FULL MID  0   box=32000873 whls=ROUGH pos=1111 grip=111 errs=(4, 1012) 42%", "param1": -16, "robot_id": 7, "start_tick": 1241, "task_id": 197203, "tick": 1241, "time": "2026-07-16T10:17:20"}
-- RANDOM_ROWS: safety_events
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 2597, "id": 18578, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 2596, 'finished_tick': 2597, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T09:34:28.495508Z', 'ready_for_next_command': 4, 'battery_charge': 65, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T09:34:28.495508Z', 'ready_for_next_command': 2, 'battery_charge': 65, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 65%", "param1": 1005, "robot_id": 6, "start_tick": 2596, "task_id": 164688, "tick": 2596, "time": "2026-03-20T08:34:29"}
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 3603, "id": 19584, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 3602, 'finished_tick': 3603, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:02:09.547550Z', 'ready_for_next_command': 4, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.603, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.497, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:02:09.547550Z', 'ready_for_next_command': 2, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.603, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.497, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 64%", "param1": 1005, "robot_id": 6, "start_tick": 3602, "task_id": 164688, "tick": 3602, "time": "2026-03-20T09:02:10"}
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 4093, "id": 20074, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 4092, 'finished_tick': 4093, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:15:39.302720Z', 'ready_for_next_command': 4, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:15:39.302720Z', 'ready_for_next_command': 2, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.252, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 64%", "param1": 1005, "robot_id": 6, "start_tick": 4092, "task_id": 164688, "tick": 4092, "time": "2026-03-20T09:15:39"}
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 4324, "id": 20305, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 4323, 'finished_tick': 4324, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:22:00.978378Z', 'ready_for_next_command': 4, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.601, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.253, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:22:00.978378Z', 'ready_for_next_command': 2, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.601, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.253, 'encoder_wheel_4': -2643.496, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 64%", "param1": 1005, "robot_id": 6, "start_tick": 4323, "task_id": 164688, "tick": 4323, "time": "2026-03-20T09:22:01"}
-- row: {"box_id": null, "check_name": "InterrobotCollisionsChecker", "command_id": "MOVE", "finished_tick": 447, "id": 17715, "json_data": "{'command_id': 'MOVE', 'param1': 4, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': 2237, 'start_tick': 440, 'finished_tick': 447, 'start_state': {'robot_id': 5, 'timestamp': '2026-03-12T11:13:37.444141Z', 'ready_for_next_command': 2, 'battery_charge': 83, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 2, 'x': 4, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002118, 'encoder_wheel_1': 7004.72, 'encoder_wheel_2': 11947.793, 'encoder_wheel_3': -11537.51, 'encoder_wheel_4': -7007.261, 'steering_encoder_deg': 91.754, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 10680, 'y_mm': 2437}, 'finish_state': {'robot_id': 5, 'timestamp': '2026-03-12T11:13:42.244141Z', 'ready_for_next_command': 2, 'battery_charge': 83, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 2, 'x': 4, 'y': 5, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002118, 'encoder_wheel_1': 7004.72, 'encoder_wheel_2': 11947.793, 'encoder_wheel_3': -11537.51, 'encoder_wheel_4': -7007.261, 'steering_encoder_deg': 91.754, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 10680, 'y_mm': 2437}, 'expected_duration_s': 4.8, 'task_id': 158245, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "IRC: Robot 5 is colliding with another robot for action NEW| 440:447 |T158245|Robot 5 MOVE to X=4 Y=5 2237mm || 5 :READY  4 1  0 steer=Y head=E(0  ) lift=TOP(    0mm) grip=FULL MID  0   box=32002118 pos=11111 grip=1001 83%", "param1": 4, "robot_id": 5, "start_tick": 440, "task_id": 158245, "tick": 387, "time": "2026-03-12T10:13:18"}
-- id: unique identifier, nulls=0, non_nulls=9713, distinct=9713
-- id numeric: min=17177, max=26889, average=22033.0000, median=22033.0000
-- check_name: nulls=0, non_nulls=9713, distinct=7
-- check_name values: InterrobotCollisionsChecker=4677, CMDConstraintsCheck=3343, StartStateCheck=1222, MoveWithLoweredLiftCheck=399, LiftSafetyChecker=60, LiftDownToInactivePort=7, MoveOutboundCheck=5
-- message: nulls=0, non_nulls=9713, distinct=2751
-- tick: nulls=0, non_nulls=9713, distinct=4079
-- tick numeric: min=1, max=12592, average=1944.8157, median=1160.0000
-- time: nulls=0, non_nulls=9713, distinct=8362
-- time top_values: 2026-03-18 10:07:01=14, 2026-03-18 10:07:22=14, 2026-03-18 10:08:04=14, 2026-03-18 10:08:25=14, 2026-03-18 10:08:46=14, 2026-05-19 08:46:02=12, 2026-05-19 08:46:07=12, 2026-05-19 08:46:09=12, 2026-03-18 10:35:46=10, 2026-05-20 08:58:39=10
-- robot_id: nulls=0, non_nulls=9713, distinct=7
-- robot_id numeric: min=1, max=8, average=6.0058, median=6.0000
-- robot_id values: 6=3679, 7=3452, 5=1884, 1=387, 8=268, 3=27, 4=16
-- task_id: nulls=256, non_nulls=9457, distinct=984
-- task_id numeric: min=155269, max=197255, average=174020.9368, median=165448.0000
-- box_id: nulls=5489, non_nulls=4224, distinct=248
-- box_id numeric: min=17000047, max=32002154, average=31514225.5258, median=32000777.0000
-- command_id: nulls=0, non_nulls=9713, distinct=12
-- command_id values: RECOVER=6125, MOVE=1462, IDLE=446, LIFT=400, ROTATE_WHEELS=338, STOP=300, TAKE_BOX=277, PUT_BOX=148, EXTEND_GRIPPER=87, ACK_ERROR=75, UNCLENCH=35, CHECK_ROBOT_READY=20
-- param1: nulls=0, non_nulls=9713, distinct=117
-- param1 numeric: min=-68, max=4688, average=756.4616, median=1005.0000
-- start_tick: nulls=0, non_nulls=9713, distinct=4314
-- start_tick numeric: min=1, max=12592, average=1952.7843, median=1160.0000
-- finished_tick: nulls=0, non_nulls=9713, distinct=4326
-- finished_tick numeric: min=2, max=12594, average=1985.9318, median=1163.0000
-- json_data: nulls=0, non_nulls=9713, distinct=9437


CREATE TABLE `simulation_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `n_tasks` int(11) NOT NULL,
  `interval_s` float NOT NULL,
  `port_dwell_time_s` float NOT NULL,
  `use_frequency_groups` tinyint(1) NOT NULL,
  `status` varchar(30) NOT NULL,
  `created_at` timestamp NOT NULL,
  `tasks_sent` int(11) NOT NULL,
  `tasks_completed` int(11) NOT NULL,
  `error_message` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: simulation_session


CREATE TABLE `simulation_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_time_s` double NOT NULL,
  `type` varchar(30) NOT NULL,
  `box_id` int(11) NOT NULL,
  `port_x` int(11) NOT NULL,
  `port_y` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `units` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: simulation_task


CREATE TABLE `stack` (
  `id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `type` varchar(30) NOT NULL,
  `max_stack_height_mm` int(11) NOT NULL,
  `lift_to_stack_bottom_mm` int(11) NOT NULL,
  `short_port_id` int(11) NOT NULL,
  `label` varchar(128) NOT NULL,
  `mlns_port_type` varchar(30) NOT NULL,
  `lift_tolerance` int(11) NOT NULL,
  `gripper_extension_mm` int(11) NOT NULL,
  `future_mlns_port_type` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `stack_unique_position` (`x`,`y`,`level`),
  UNIQUE KEY `short_port_id` (`short_port_id`),
  KEY `ix_stack_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=3744
-- LATEST_ROWS: stack
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 3744, "label": "", "level": 3, "lift_to_stack_bottom_mm": 1555, "lift_tolerance": 45, "max_stack_height_mm": 806, "mlns_port_type": "M", "short_port_id": 4745, "type": "UNSTORABLE", "x": 71, "y": 12}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 3743, "label": "", "level": 2, "lift_to_stack_bottom_mm": 1890, "lift_tolerance": 45, "max_stack_height_mm": 1247, "mlns_port_type": "M", "short_port_id": 4744, "type": "UNSTORABLE", "x": 71, "y": 12}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 3742, "label": "", "level": 1, "lift_to_stack_bottom_mm": 1925, "lift_tolerance": 45, "max_stack_height_mm": 1260, "mlns_port_type": "M", "short_port_id": 4743, "type": "UNSTORABLE", "x": 71, "y": 12}
-- RANDOM_ROWS: stack
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 1701, "label": "", "level": 3, "lift_to_stack_bottom_mm": 1555, "lift_tolerance": 45, "max_stack_height_mm": 806, "mlns_port_type": "M", "short_port_id": 2702, "type": "UNSTORABLE", "x": 19, "y": 7}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 2576, "label": "", "level": 2, "lift_to_stack_bottom_mm": 1890, "lift_tolerance": 45, "max_stack_height_mm": 1247, "mlns_port_type": "M", "short_port_id": 3577, "type": "UNSTORABLE", "x": 42, "y": 0}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 3123, "label": "", "level": 3, "lift_to_stack_bottom_mm": 1555, "lift_tolerance": 45, "max_stack_height_mm": 806, "mlns_port_type": "M", "short_port_id": 4124, "type": "UNSTORABLE", "x": 56, "y": 0}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 2769, "label": "", "level": 3, "lift_to_stack_bottom_mm": 1555, "lift_tolerance": 45, "max_stack_height_mm": 806, "mlns_port_type": "M", "short_port_id": 3770, "type": "UNSTORABLE", "x": 46, "y": 12}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 2484, "label": "", "level": 3, "lift_to_stack_bottom_mm": 1555, "lift_tolerance": 45, "max_stack_height_mm": 806, "mlns_port_type": "M", "short_port_id": 3485, "type": "UNSTORABLE", "x": 39, "y": 8}
-- id: unique identifier, nulls=0, non_nulls=3744, distinct=3744
-- id numeric: min=1, max=3744, average=1872.5000, median=1872.5000
-- x: nulls=0, non_nulls=3744, distinct=72
-- x numeric: min=0, max=71, average=35.5000, median=35.5000
-- x top_values: 0=52, 1=52, 2=52, 3=52, 4=52, 5=52, 6=52, 7=52, 8=52, 9=52
-- y: nulls=0, non_nulls=3744, distinct=13
-- y numeric: min=0, max=12, average=6.0000, median=6.0000
-- y values: 0=288, 1=288, 2=288, 3=288, 4=288, 5=288, 6=288, 7=288, 8=288, 9=288, 10=288, 11=288, 12=288
-- level: nulls=0, non_nulls=3744, distinct=4
-- level numeric: min=0, max=3, average=1.5000, median=1.5000
-- level values: 0=936, 1=936, 2=936, 3=936
-- type: nulls=0, non_nulls=3744, distinct=4
-- type values: UNSTORABLE=3671, STORABLE=67, PICKING_PORT=4, BALCONY_PORT=2
-- max_stack_height_mm: nulls=0, non_nulls=3744, distinct=5
-- max_stack_height_mm numeric: min=806, max=1600, average=1228.2783, median=1260.0000
-- max_stack_height_mm values: 806=936, 1260=936, 1600=936, 1247=934, 1300=2
-- lift_to_stack_bottom_mm: nulls=0, non_nulls=3744, distinct=7
-- lift_to_stack_bottom_mm numeric: min=640, max=2385, average=1937.0700, median=1890.0000
-- lift_to_stack_bottom_mm values: 1555=936, 1890=936, 1925=934, 2385=923, 2365=9, 1500=4, 640=2
-- short_port_id: unique identifier, nulls=0, non_nulls=3744, distinct=3744
-- short_port_id numeric: min=1, max=4745, average=2871.4396, median=2873.5000
-- label: nulls=0, non_nulls=3744, distinct=1
-- label values: =3744
-- mlns_port_type: nulls=0, non_nulls=3744, distinct=2
-- mlns_port_type values: M=3741, P=3
-- lift_tolerance: nulls=0, non_nulls=3744, distinct=1
-- lift_tolerance numeric: min=45, max=45, average=45.0000, median=45.0000
-- lift_tolerance values: 45=3744
-- gripper_extension_mm: nulls=0, non_nulls=3744, distinct=3
-- gripper_extension_mm numeric: min=0, max=196, average=0.2553, median=0.0000
-- gripper_extension_mm values: 0=3738, 196=4, 86=2
-- future_mlns_port_type: all NULL


CREATE TABLE `system_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_time` timestamp NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2129 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=2128
-- LATEST_ROWS: system_session
-- row: {"id": 2128, "start_time": "2026-07-17T10:06:12"}
-- row: {"id": 2127, "start_time": "2026-07-16T09:27:48"}
-- row: {"id": 2126, "start_time": "2026-07-16T06:43:42"}
-- RANDOM_ROWS: system_session
-- row: {"id": 869, "start_time": "2025-09-19T07:46:19"}
-- row: {"id": 1680, "start_time": "2026-03-03T12:42:22"}
-- row: {"id": 718, "start_time": "2025-08-28T13:41:58"}
-- row: {"id": 102, "start_time": "2025-06-09T06:02:14"}
-- row: {"id": 1474, "start_time": "2026-01-29T09:55:28"}
-- id: unique identifier, nulls=0, non_nulls=2128, distinct=2128
-- id numeric: min=1, max=2128, average=1064.5000, median=1064.5000
-- start_time: nulls=0, non_nulls=2128, distinct=2128


CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(30) NOT NULL,
  `status` varchar(30) NOT NULL,
  `create_ts` timestamp NOT NULL,
  `child_storage_task_id` int(11) DEFAULT NULL,
  `delayed_until_ts` timestamp NULL DEFAULT NULL,
  `finished_ts` timestamp NULL DEFAULT NULL,
  `plan_ts` timestamp NULL DEFAULT NULL,
  `last_replan_ts` timestamp NULL DEFAULT NULL,
  `start_exec_ts` timestamp NULL DEFAULT NULL,
  `box_id` int(11) DEFAULT NULL,
  `balcony_stack_id` int(11) DEFAULT NULL,
  `n_boxes_ontop` int(11) DEFAULT NULL,
  `robot_id` int(11) DEFAULT NULL,
  `charging_station_id` int(11) DEFAULT NULL,
  `port_stack_id` int(11) DEFAULT NULL,
  `predicted_picking_time_s` double DEFAULT NULL,
  `batch_id` int(11) DEFAULT NULL,
  `storage_level` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `box_id` (`box_id`),
  KEY `balcony_stack_id` (`balcony_stack_id`),
  KEY `charging_station_id` (`charging_station_id`),
  KEY `port_stack_id` (`port_stack_id`),
  KEY `batch_id` (`batch_id`),
  KEY `ix_task_status` (`status`),
  KEY `ix_task_type` (`type`),
  KEY `ix_task_status_type` (`status`,`type`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`),
  CONSTRAINT `task_ibfk_2` FOREIGN KEY (`balcony_stack_id`) REFERENCES `stack` (`id`),
  CONSTRAINT `task_ibfk_3` FOREIGN KEY (`charging_station_id`) REFERENCES `charging_station` (`id`),
  CONSTRAINT `task_ibfk_4` FOREIGN KEY (`port_stack_id`) REFERENCES `stack` (`id`),
  CONSTRAINT `task_ibfk_5` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`),
  CONSTRAINT `c_box_storage` CHECK (`type` <> _utf8mb4'BOX_STORAGE' or `box_id` is not null),
  CONSTRAINT `c_charging` CHECK (`type` <> _utf8mb4'CHARGE' or `robot_id` is not null and `charging_station_id` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=197264 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=50564
-- LATEST_ROWS: task
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000840, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-16T10:30:16", "delayed_until_ts": null, "finished_ts": null, "id": 197263, "last_replan_ts": null, "n_boxes_ontop": null, "plan_ts": null, "port_stack_id": 522, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": null, "status": "QUEUED", "storage_level": null, "type": "MOVE_BOX"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000604, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-16T10:30:15", "delayed_until_ts": null, "finished_ts": null, "id": 197262, "last_replan_ts": null, "n_boxes_ontop": null, "plan_ts": null, "port_stack_id": 379, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": null, "status": "QUEUED", "storage_level": null, "type": "MOVE_BOX"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000259, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-16T10:30:14", "delayed_until_ts": null, "finished_ts": null, "id": 197261, "last_replan_ts": null, "n_boxes_ontop": null, "plan_ts": null, "port_stack_id": 184, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": null, "status": "QUEUED", "storage_level": null, "type": "MOVE_BOX"}
-- RANDOM_ROWS: task
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-01T12:57:31", "delayed_until_ts": null, "finished_ts": "2026-07-01T12:57:32", "id": 188379, "last_replan_ts": "2026-07-01T12:57:31", "n_boxes_ontop": null, "plan_ts": "2026-07-01T12:57:31", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 5, "start_exec_ts": "2026-07-01T12:57:31", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-05-06T10:30:00", "delayed_until_ts": null, "finished_ts": "2026-05-06T10:30:00", "id": 173523, "last_replan_ts": "2026-05-06T10:30:00", "n_boxes_ontop": null, "plan_ts": "2026-05-06T10:30:00", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 6, "start_exec_ts": "2026-05-06T10:30:00", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000479, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-03-20T06:50:04", "delayed_until_ts": "2026-03-20T07:26:00", "finished_ts": null, "id": 164522, "last_replan_ts": null, "n_boxes_ontop": 0, "plan_ts": "2026-03-20T07:07:39", "port_stack_id": 933, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": "2026-03-20T07:07:39", "status": "CANCELLED", "storage_level": 2, "type": "EXTRACT_BOX"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-01T16:00:02", "delayed_until_ts": null, "finished_ts": "2026-07-01T16:00:02", "id": 189635, "last_replan_ts": "2026-07-01T16:00:02", "n_boxes_ontop": null, "plan_ts": "2026-07-01T16:00:02", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 5, "start_exec_ts": "2026-07-01T16:00:02", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000844, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-07-15T13:47:04", "delayed_until_ts": null, "finished_ts": "2026-07-15T13:48:57", "id": 196887, "last_replan_ts": "2026-07-15T13:48:42", "n_boxes_ontop": null, "plan_ts": "2026-07-15T13:47:06", "port_stack_id": 496, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": "2026-07-15T13:47:06", "status": "COMPLETED", "storage_level": null, "type": "MOVE_BOX"}
-- id: unique identifier, nulls=0, non_nulls=50564, distinct=50564
-- id numeric: min=273, max=197263, average=168759.9750, median=171981.5000
-- type: nulls=0, non_nulls=50564, distinct=8
-- type values: RECOVER_ROBOT=30993, PREPARE_ROBOTS=8647, MOVE_BOX=6301, BOX_STORAGE=3091, MOVE_ROBOT=951, EXTRACT_BOX=288, CHARGE=157, EXTRACT_FOR_PICK=136
-- status: nulls=0, non_nulls=50564, distinct=4
-- status values: COMPLETED=37739, CANCELLED=12816, QUEUED=5, FAILED=4
-- create_ts: nulls=0, non_nulls=50564, distinct=43739
-- child_storage_task_id: all NULL
-- delayed_until_ts: nulls=49084, non_nulls=1480, distinct=1418
-- finished_ts: nulls=3573, non_nulls=46991, distinct=40434
-- plan_ts: nulls=8118, non_nulls=42446, distinct=38705
-- last_replan_ts: nulls=25136, non_nulls=25428, distinct=22400
-- start_exec_ts: nulls=8608, non_nulls=41956, distinct=38473
-- box_id: nulls=40748, non_nulls=9816, distinct=727
-- box_id numeric: min=101, max=32005990, average=30417010.0253, median=32000599.0000
-- box_id top_values: 32000183=226, 17000219=118, 32000667=116, 32000604=67, 32000546=66, 32001146=64, 32000845=63, 32000846=54, 32000876=54, 32000162=53
-- balcony_stack_id: all NULL
-- n_boxes_ontop: nulls=47173, non_nulls=3391, distinct=5
-- n_boxes_ontop numeric: min=0, max=4, average=0.0395, median=0.0000
-- n_boxes_ontop values: 0=3288, 1=81, 2=15, 3=5, 4=2
-- robot_id: nulls=18457, non_nulls=32107, distinct=7
-- robot_id numeric: min=1, max=8, average=5.5840, median=6.0000
-- robot_id values: 5=12416, 7=8710, 6=6320, 1=1748, 8=1444, 3=861, 4=608
-- charging_station_id: nulls=50407, non_nulls=157, distinct=4
-- charging_station_id numeric: min=1, max=4, average=1.4650, median=1.0000
-- charging_station_id values: 1=120, 3=18, 2=10, 4=9
-- port_stack_id: nulls=43614, non_nulls=6950, distinct=635
-- port_stack_id numeric: min=41, max=3660, average=778.4912, median=618.0000
-- port_stack_id top_values: 927=340, 1253=198, 929=151, 171=108, 931=104, 67=95, 54=94, 907=89, 366=88, 119=81
-- predicted_picking_time_s: nulls=49063, non_nulls=1501, distinct=2
-- predicted_picking_time_s numeric: min=0e-10, max=5.0000000000, average=0.413058, median=0
-- predicted_picking_time_s values: 0e-10=1377, 5.0000000000=124
-- batch_id: nulls=50438, non_nulls=126, distinct=46
-- batch_id numeric: min=151, max=214, average=188.8016, median=190.0000
-- batch_id top_values: 204=22, 184=8, 198=8, 181=6, 183=6, 188=5, 190=4, 162=3, 163=3, 166=3
-- storage_level: nulls=47895, non_nulls=2669, distinct=4
-- storage_level numeric: min=0, max=3, average=1.0937, median=1.0000
-- storage_level values: 0=1284, 3=643, 1=494, 2=248


CREATE TABLE `task_alter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL,
  `task_id` int(11) NOT NULL,
  `port_stack_id` int(11) DEFAULT NULL,
  `status` enum('new','done') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `port_stack_id` (`port_stack_id`),
  CONSTRAINT `task_alter_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`),
  CONSTRAINT `task_alter_ibfk_2` FOREIGN KEY (`port_stack_id`) REFERENCES `stack` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: task_alter


CREATE TABLE `timing_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `a_mpss` float NOT NULL,
  `v_max_mps` float NOT NULL,
  `tick_s` float NOT NULL,
  `unclench_s` float NOT NULL,
  `squeeze_s` float NOT NULL,
  `rotate_wheel_s` float NOT NULL,
  `rotate_head_180_slow_s` float NOT NULL,
  `rotate_head_90_slow_s` float NOT NULL,
  `rotate_head_270_slow_s` float NOT NULL,
  `rotate_head_180_fast_s` float NOT NULL,
  `rotate_head_90_fast_s` float NOT NULL,
  `rotate_head_270_fast_s` float NOT NULL,
  `rotate_head_is_slow` tinyint(1) NOT NULL,
  `liftup_speed_mmps` int(11) NOT NULL,
  `liftup_accel_mmps` int(11) NOT NULL,
  `liftdown_speed_mmps` int(11) NOT NULL,
  `liftdown_accel_mmps` int(11) NOT NULL,
  `stop_s` float NOT NULL,
  `reset_error_s` float NOT NULL,
  `check_port_s` float NOT NULL,
  `gripper_200mm_extention_s` float DEFAULT 4.8,
  `final_roll_time_per_cell_s` double DEFAULT 0.13,
  `undershoot_per_cell_mm` int(11) DEFAULT 4,
  `recover_move_speed_mmps` float DEFAULT 40,
  `recover_steer_s` float DEFAULT 4,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: timing_params
-- row: {"a_mpss": 0.5, "check_port_s": 1.0, "final_roll_time_per_cell_s": "0.1300000000", "gripper_200mm_extention_s": 3.5, "id": 1, "liftdown_accel_mmps": 250, "liftdown_speed_mmps": 220, "liftup_accel_mmps": 200, "liftup_speed_mmps": 220, "recover_move_speed_mmps": 20.0, "recover_steer_s": 4.0, "reset_error_s": 1.0, "rotate_head_180_fast_s": 16.9, "rotate_head_180_slow_s": 10.0, "rotate_head_270_fast_s": 16.0, "rotate_head_270_slow_s": 15.0, "rotate_head_90_fast_s": 10.0, "rotate_head_90_slow_s": 5.0, "rotate_head_is_slow": 0, "rotate_wheel_s": 2.8, "squeeze_s": 0.2, "stop_s": 0.2, "tick_s": 0.6, "unclench_s": 1.33, "undershoot_per_cell_mm": 4, "v_max_mps": 1.5}


CREATE TABLE `timings_put_box` (
  `lift_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`lift_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=3
-- ALL_ROWS: timings_put_box
-- row: {"lift_mm": 1, "time_s": 1.0}
-- row: {"lift_mm": 820, "time_s": 8.2}
-- row: {"lift_mm": 2060, "time_s": 14.5}


CREATE TABLE `timings_take_box` (
  `lift_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`lift_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=3
-- ALL_ROWS: timings_take_box
-- row: {"lift_mm": 1, "time_s": 1.0}
-- row: {"lift_mm": 820, "time_s": 7.5}
-- row: {"lift_mm": 2060, "time_s": 12.5}


CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `role` varchar(30) NOT NULL,
  `pwd_hash` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: user
-- row: {"id": 1, "name": "dive", "pwd_hash": "[REDACTED]", "role": "ADMIN"}


CREATE TABLE `warehouse_fullness` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fullness` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `registering_time` timestamp NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_warehouse_fullness_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=0
-- ALL_ROWS: warehouse_fullness
