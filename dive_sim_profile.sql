-- db-snooper
-- version: 0.1.0
-- dialect: mariadb
-- database: dive_sim
-- url: mariadb+mariadbconnector://dive_simmer:***@localhost:3306/dive_sim

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
  KEY `ix_action_history_robot_id_id` (`robot_id`)
) ENGINE=InnoDB AUTO_INCREMENT=542476 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=204212
-- LATEST_ROWS: action_history
-- row: {"box_id": null, "command": "TASK_DONE", "dist_mm": 0, "expected_duration_s": 0.01, "id": 542475, "param1": 7, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 1524, "start_time": "2026-06-25T14:48:14.673000", "task_id": 187064}
-- row: {"box_id": null, "command": "TASK_START", "dist_mm": 0, "expected_duration_s": 0.01, "id": 542474, "param1": 187064, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 1524, "start_time": "2026-06-25T14:48:14.666000", "task_id": 187064}
-- row: {"box_id": null, "command": "TASK_DONE", "dist_mm": 0, "expected_duration_s": 0.01, "id": 542473, "param1": -1, "param2": 0, "param3": 0, "param4": 0, "param5": null, "robot_id": 7, "start_tick": 1522, "start_time": "2026-06-25T14:48:13.491000", "task_id": 187068}
-- RANDOM_ROWS: action_history
-- row: {"box_id": null, "command": "TASK_DONE", "dist_mm": 0, "expected_duration_s": 0.01, "id": 378616, "param1": -1, "param2": 0, "param3": 0, "param4": null, "param5": null, "robot_id": 5, "start_tick": 1174, "start_time": "2026-03-12T07:41:50.275000", "task_id": 157834}
-- row: {"box_id": null, "command": "EXTEND_GRIPPER", "dist_mm": 0, "expected_duration_s": 4.832, "id": 428025, "param1": 196, "param2": 0, "param3": 0, "param4": null, "param5": null, "robot_id": 8, "start_tick": 40, "start_time": "2026-04-08T14:16:27.397000", "task_id": 167836}
-- row: {"box_id": null, "command": "TASK_DONE", "dist_mm": 0, "expected_duration_s": 0.01, "id": 348417, "param1": -1, "param2": 0, "param3": 0, "param4": null, "param5": null, "robot_id": 1, "start_tick": 715, "start_time": "2026-03-04T08:31:09.646000", "task_id": 150292}
-- row: {"box_id": null, "command": "TASK_START", "dist_mm": 0, "expected_duration_s": 0.01, "id": 374818, "param1": 157288, "param2": 0, "param3": 0, "param4": null, "param5": null, "robot_id": 4, "start_tick": 941, "start_time": "2026-03-11T13:04:35.405000", "task_id": 157288}
-- row: {"box_id": null, "command": "TASK_START", "dist_mm": 0, "expected_duration_s": 0.01, "id": 382420, "param1": 158765, "param2": 0, "param3": 0, "param4": null, "param5": null, "robot_id": 4, "start_tick": 204, "start_time": "2026-03-12T10:38:33.182000", "task_id": 158765}
-- id: unique values=204212, range=338264..542475
-- robot_id: nulls=0, non_nulls=204212, distinct=7
-- robot_id numeric: min=1, median=6.0000, max=8
-- robot_id values: 5=67391, 7=60401, 6=23842, 8=21560, 1=12618, 3=12116, 4=6284
-- start_time: nulls=0, non_nulls=204212, distinct=204212
-- start_tick: nulls=0, non_nulls=204212, distinct=11857
-- start_tick numeric: min=1, median=835.0000, max=15446
-- start_tick top_values: 1=1683, 2=698, 3=575, 10=469, 4=370, 15=329, 21=328, 5=325, 6=314, 16=306
-- expected_duration_s: nulls=0, non_nulls=204212, distinct=1890
-- expected_duration_s numeric: min=0.01, median=0.01, max=2151.6
-- expected_duration_s top_values: 0.01=114210, 2.8=13463, 1.33=6053, 3=5058, 3.6=2582, 1=2447, 2.4=2271, 4.8=1717, 4.832=1442, 7.2=1162
-- command: nulls=0, non_nulls=204212, distinct=25
-- command top_values: TASK_START=53433, TASK_DONE=31238, MOVE=25778, LIFT=25402, ROTATE_WHEELS=13463, VERIFY_BOX_RFID=8354, UNRESERVE_BOX=6477, UNCLENCH=6053, RECOVER=5290, MARK_NOT_IN_USE=5202
-- param1: nulls=0, non_nulls=204212, distinct=35883
-- param1 numeric: min=-70, median=17.0000, max=32005990
-- param1 top_values: -1=28893, 0=27428, 1=10798, 2=9322, 5=7371, 7=3126, 1400=2861, 1005=2236, 71=2191, -2=1789
-- param2: nulls=0, non_nulls=204212, distinct=541
-- param2 numeric: min=-2025, median=0.0000, max=4803
-- param2 top_values: 0=191700, 1=3103, 3=1636, 2=1043, 2025=810, 140=620, 5=583, 650=573, 7=550, 9=371
-- param3: nulls=0, non_nulls=204212, distinct=4
-- param3 numeric: min=0, median=0.0000, max=300
-- param3 values: 0=199500, 300=2861, 40=1086, 20=765
-- dist_mm: nulls=0, non_nulls=204212, distinct=463
-- dist_mm numeric: min=-29220, median=0.0000, max=29220
-- dist_mm top_values: 0=176198, 680=2056, -680=1723, -480=1419, 480=1333, -1360=863, 1360=815, -2237=579, 2237=530, 2060=495
-- task_id: nulls=0, non_nulls=204212, distinct=34933
-- task_id numeric: min=147626, median=169813.5000, max=187068
-- task_id top_values: 153260=877, 178027=449, 150772=360, 172983=350, 184460=348, 156782=295, 163559=274, 148412=247, 150761=241, 166692=232
-- param4: nulls=184272, non_nulls=19940, distinct=2
-- param4 numeric: min=0, median=0.0000, max=100
-- param4 values: 0=18379, 100=1561
-- box_id: nulls=202648, non_nulls=1564, distinct=242
-- box_id numeric: min=-1, median=32000619.0000, max=32002114
-- box_id top_values: 32000543=187, 32000619=132, 32000546=61, 32000622=45, 32001032=35, 32001156=33, 17000177=28, 32000627=24, 32001035=24, 32000862=20
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
  CONSTRAINT `action_status_history_ibfk_1` FOREIGN KEY (`action_history_id`) REFERENCES `action_history` (`id`),
  CONSTRAINT `action_status_history_ibfk_2` FOREIGN KEY (`state_history_id`) REFERENCES `robot_state_history` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=943812 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=551830
-- LATEST_ROWS: action_status_history
-- row: {"action_history_id": 542475, "action_status": "DONE", "id": 943811, "state_history_id": 1187393, "tick": 1524, "time": "2026-06-25T14:48:14.691000"}
-- row: {"action_history_id": 542474, "action_status": "DONE", "id": 943810, "state_history_id": 1187392, "tick": 1524, "time": "2026-06-25T14:48:14.683000"}
-- row: {"action_history_id": 542475, "action_status": "SCHEDULED", "id": 943809, "state_history_id": null, "tick": 1524, "time": "2026-06-25T14:48:14.678000"}
-- RANDOM_ROWS: action_status_history
-- row: {"action_history_id": 452107, "action_status": "SCHEDULED", "id": 642159, "state_history_id": 941273, "tick": 385, "time": "2026-04-21T05:40:08.572000"}
-- row: {"action_history_id": 454802, "action_status": "SCHEDULED", "id": 651171, "state_history_id": 948554, "tick": 4541, "time": "2026-04-21T07:04:34.787000"}
-- row: {"action_history_id": 497682, "action_status": "DONE", "id": 791991, "state_history_id": 1060284, "tick": 2417, "time": "2026-05-21T11:13:22.138000"}
-- row: {"action_history_id": 486613, "action_status": "DONE", "id": 757247, "state_history_id": 1034777, "tick": 167, "time": "2026-05-19T13:29:26.198000"}
-- row: {"action_history_id": 378241, "action_status": "SCHEDULED", "id": 429906, "state_history_id": null, "tick": 701, "time": "2026-03-12T07:32:04.543000"}
-- id: unique values=551830, range=391982..943811
-- action_history_id: nulls=0, non_nulls=551830, distinct=179744
-- action_history_id numeric: min=362732, median=459736.0000, max=542475
-- action_history_id top_values: 423373=4, 423378=4, 423383=4, 423384=4, 423386=4, 423387=4, 423388=4, 423391=4, 423392=4, 423395=4
-- tick: nulls=0, non_nulls=551830, distinct=12029
-- tick numeric: min=1, median=854.0000, max=15446
-- tick top_values: 1=4069, 2=1772, 3=1463, 10=1133, 4=861, 21=855, 20=852, 15=839, 5=837, 22=834
-- time: nulls=0, non_nulls=551830, distinct=551830
-- action_status: nulls=0, non_nulls=551830, distinct=5
-- action_status values: SCHEDULED=298848, DONE=165650, EXEC=73332, FAILED=12558, FAILED_TIMEOUT=1442
-- state_history_id: nulls=98520, non_nulls=453310, distinct=453310
-- state_history_id numeric: min=734084, median=960738.5000, max=1187393


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
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=182
-- LATEST_ROWS: batch
-- row: {"create_ts": "2026-03-26T08:59:58", "finish_ts": "2026-03-26T09:03:26", "frozen_ts": null, "id": 208, "mlns_id": "BUNL04", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-26T08:51:54", "finish_ts": "2026-03-26T08:55:23", "frozen_ts": null, "id": 207, "mlns_id": "BUNL03", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-26T08:43:26", "finish_ts": "2026-03-26T08:46:51", "frozen_ts": null, "id": 206, "mlns_id": "BUNL02", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- RANDOM_ROWS: batch
-- row: {"create_ts": "2025-12-15T15:19:14", "finish_ts": "2025-12-15T15:22:41", "frozen_ts": null, "id": 107, "mlns_id": "101", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-11T15:22:49", "finish_ts": "2026-03-11T15:45:06", "frozen_ts": null, "id": 167, "mlns_id": "tbh12", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2026-03-18T10:56:59", "finish_ts": "2026-03-18T10:59:48", "frozen_ts": null, "id": 196, "mlns_id": "tbh9010", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2025-12-03T14:52:42", "finish_ts": "2025-12-03T15:53:09", "frozen_ts": null, "id": 75, "mlns_id": "test_voll_3", "mlns_port_type": "E", "priority": 0, "status": "COMPLETED"}
-- row: {"create_ts": "2025-11-19T07:39:58", "finish_ts": "2025-11-19T08:05:05", "frozen_ts": null, "id": 46, "mlns_id": "Dive04", "mlns_port_type": "A", "priority": 0, "status": "COMPLETED"}
-- id: unique values=182, range=4..208
-- mlns_id: unique values=182
-- create_ts: nulls=0, non_nulls=182, distinct=181
-- create_ts top_values: 2025-11-24 12:20:27=2, 2025-08-29 12:22:35=1, 2025-10-02 07:39:28=1, 2025-10-02 07:42:47=1, 2025-10-02 07:44:43=1, 2025-10-02 07:46:47=1, 2025-10-02 07:48:17=1, 2025-10-28 08:01:03=1, 2025-11-06 09:48:46=1, 2025-11-06 12:28:47=1
-- priority: nulls=0, non_nulls=182, distinct=7
-- priority numeric: min=0, median=0.0000, max=9
-- priority values: 0=121, 2=26, 5=14, 7=11, 3=8, 1=1, 9=1
-- finish_ts: nulls=13, non_nulls=169, distinct=158
-- finish_ts top_values: 2025-10-02 08:00:31=4, 2025-11-25 07:22:02=4, 2025-12-10 09:29:30=3, 2026-03-12 11:11:09=3, 2025-12-03 15:53:09=2, 2025-08-29 12:38:28=1, 2025-10-02 08:21:21=1, 2025-10-30 08:11:02=1, 2025-11-06 13:53:38=1, 2025-11-06 13:59:13=1
-- frozen_ts: nulls=108, non_nulls=74, distinct=63
-- frozen_ts top_values: 2025-11-24 12:22:25=5, 2025-10-02 08:00:31=4, 2026-03-12 11:11:09=3, 2025-11-20 14:09:10=2, 2026-03-18 11:15:04=2, 2025-10-30 08:11:02=1, 2025-11-06 09:48:47=1, 2025-11-06 12:28:48=1, 2025-11-07 11:36:57=1, 2025-11-07 11:47:06=1
-- mlns_port_type: nulls=0, non_nulls=182, distinct=4
-- mlns_port_type values: A=131, E=34, M=9, F=8
-- status: nulls=0, non_nulls=182, distinct=3
-- status values: COMPLETED=116, CANCELLED=54, INCOMPLETED=12


CREATE TABLE `batch_box_association` (
  `batch_id` int(11) NOT NULL,
  `box_id` int(11) NOT NULL,
  PRIMARY KEY (`batch_id`,`box_id`),
  KEY `box_id` (`box_id`),
  CONSTRAINT `batch_box_association_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`) ON DELETE CASCADE,
  CONSTRAINT `batch_box_association_ibfk_2` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=382
-- LATEST_ROWS: batch_box_association
-- row: {"batch_id": 208, "box_id": 17000038}
-- row: {"batch_id": 207, "box_id": 17000038}
-- row: {"batch_id": 206, "box_id": 17000038}
-- RANDOM_ROWS: batch_box_association
-- row: {"batch_id": 156, "box_id": 32001155}
-- row: {"batch_id": 143, "box_id": 17000257}
-- row: {"batch_id": 8, "box_id": 32001162}
-- row: {"batch_id": 183, "box_id": 32000121}
-- row: {"batch_id": 62, "box_id": 32000019}
-- batch_id: unique values=171, range=5..208
-- box_id: unique values=168, range=17000038..32005989


CREATE TABLE `batch_port` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `port_short_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`),
  CONSTRAINT `batch_port_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `batch` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=22
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
) ENGINE=InnoDB AUTO_INCREMENT=40341 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=2
-- ALL_ROWS: blocked_area
-- row: {"id": 40307, "level": 0, "reason": "NOT_IN_USE", "robot_id": 5, "timestamp": "2026-06-25T14:32:42", "x_begin_mm": 1000, "x_end_mm": 1500, "y_begin_mm": 3797, "y_end_mm": 4497}
-- row: {"id": 40308, "level": 0, "reason": "NOT_IN_USE", "robot_id": 5, "timestamp": "2026-06-25T14:32:42", "x_begin_mm": 1500, "x_end_mm": 1980, "y_begin_mm": 3797, "y_end_mm": 4497}


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

-- total rows=694
-- LATEST_ROWS: box
-- row: {"cell_id": null, "height_mm": 170, "held_by_robot_id": null, "id": 99999999, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32005990, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32005989, "reserve_id": null}
-- RANDOM_ROWS: box
-- row: {"cell_id": 8650, "height_mm": 325, "held_by_robot_id": null, "id": 32001049, "reserve_id": null}
-- row: {"cell_id": 11914, "height_mm": 325, "held_by_robot_id": null, "id": 32002147, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32000100, "reserve_id": null}
-- row: {"cell_id": null, "height_mm": 325, "held_by_robot_id": null, "id": 32000491, "reserve_id": null}
-- row: {"cell_id": 1783, "height_mm": 325, "held_by_robot_id": null, "id": 32000124, "reserve_id": null}
-- id: unique values=694, range=1..99999999
-- height_mm: nulls=0, non_nulls=694, distinct=2
-- height_mm numeric: min=170, median=325.0000, max=325
-- height_mm values: 325=609, 170=85
-- reserve_id: all NULL
-- cell_id: unique values=360, range=485..16776
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
) ENGINE=InnoDB AUTO_INCREMENT=25077 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=24685
-- LATEST_ROWS: box_movement_history
-- row: {"box_id": 32000874, "id": 25076, "movement_time": "2026-06-25T14:46:44", "new_cell_id": 1344, "robot_id": 7, "task_id": 187058}
-- row: {"box_id": 32000874, "id": 25075, "movement_time": "2026-06-25T14:45:41", "new_cell_id": null, "robot_id": 7, "task_id": 187058}
-- row: {"box_id": 32000264, "id": 25074, "movement_time": "2026-06-25T14:44:11", "new_cell_id": 1343, "robot_id": 7, "task_id": 187050}
-- RANDOM_ROWS: box_movement_history
-- row: {"box_id": 32000547, "id": 20592, "movement_time": "2026-04-15T10:08:17", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 32001099, "id": 6310, "movement_time": "2025-09-08T13:15:05", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 32000490, "id": 18225, "movement_time": "2026-03-17T10:02:47", "new_cell_id": 18923, "robot_id": 1, "task_id": 162580}
-- row: {"box_id": 17000611, "id": 8366, "movement_time": "2025-09-24T12:26:55", "new_cell_id": null, "robot_id": null, "task_id": null}
-- row: {"box_id": 32001167, "id": 13799, "movement_time": "2025-12-10T12:03:38", "new_cell_id": 1323, "robot_id": 7, "task_id": 115724}
-- id: unique values=24685, range=1..25076
-- box_id: nulls=0, non_nulls=24685, distinct=694
-- box_id numeric: min=1, median=32000769.0000, max=99999999
-- box_id top_values: 32000121=262, 32000078=245, 32001146=231, 32000667=223, 32002118=221, 32001098=198, 32000223=195, 32001143=182, 32001092=180, 32005987=174
-- movement_time: nulls=0, non_nulls=24685, distinct=23675
-- movement_time top_values: 2026-03-03 16:38:51=4, 2026-03-03 16:39:10=4, 2026-03-03 16:39:29=4, 2026-03-03 16:39:48=4, 2026-03-03 16:40:46=4, 2026-03-03 16:41:05=4, 2026-03-03 16:41:24=4, 2026-03-03 16:41:43=4, 2026-03-03 16:42:41=4, 2026-03-03 16:43:00=4
-- task_id: nulls=10947, non_nulls=13738, distinct=10987
-- task_id numeric: min=47443, median=150559.5000, max=187058
-- task_id top_values: 170757=35, 183378=16, 184571=13, 183376=12, 182958=10, 177625=9, 177707=9, 142586=8, 164587=8, 164818=8
-- new_cell_id: nulls=6342, non_nulls=18343, distinct=3496
-- new_cell_id numeric: min=298, median=10187.0000, max=41119
-- new_cell_id top_values: 10187=780, 10209=522, 40789=426, 41119=271, 10231=198, 10253=104, 1299=101, 1156=78, 9969=68, 1871=67
-- robot_id: nulls=12432, non_nulls=12253, distinct=8
-- robot_id numeric: min=1, median=6.0000, max=8
-- robot_id values: 7=3791, 5=3560, 8=1561, 6=1390, 3=935, 1=509, 4=345, 2=162


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
-- row: {"box_id": 32000768, "on_error": "WARN"}
-- row: {"box_id": 32000237, "on_error": "WARN"}
-- row: {"box_id": 32001142, "on_error": "WARN"}
-- row: {"box_id": 32001195, "on_error": "WARN"}
-- row: {"box_id": 32001218, "on_error": "WARN"}
-- box_id: unique values=694, range=1..99999999
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
-- row: {"id": 38110, "stack_id": 3465, "z": 5}
-- row: {"id": 16197, "stack_id": 1473, "z": 4}
-- row: {"id": 11964, "stack_id": 1088, "z": 6}
-- row: {"id": 35582, "stack_id": 3235, "z": 7}
-- row: {"id": 16803, "stack_id": 1528, "z": 5}
-- id: unique values=41184, range=1..41184
-- stack_id: nulls=0, non_nulls=41184, distinct=3744
-- stack_id numeric: min=1, median=1872.5000, max=3744
-- stack_id top_values: 1=11, 2=11, 3=11, 4=11, 5=11, 6=11, 7=11, 8=11, 9=11, 10=11
-- z: nulls=0, non_nulls=41184, distinct=11
-- z numeric: min=0, median=5.0000, max=10
-- z values: 0=3744, 1=3744, 2=3744, 3=3744, 4=3744, 5=3744, 6=3744, 7=3744, 8=3744, 9=3744


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
-- row: {"id": 32, "mm": 480}
-- row: {"id": 33, "mm": 480}
-- row: {"id": 36, "mm": 140}
-- row: {"id": 61, "mm": 140}
-- row: {"id": 16, "mm": 140}
-- id: unique values=72, range=0..71
-- mm: nulls=0, non_nulls=72, distinct=3
-- mm numeric: min=140, median=480.0000, max=520
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

-- total rows=18031
-- LATEST_ROWS: move_robot
-- row: {"head": null, "id": 187064, "robot_id": 7, "x": 2, "y": 1}
-- row: {"head": null, "id": 187044, "robot_id": 7, "x": 7, "y": 1}
-- row: {"head": null, "id": 187038, "robot_id": 5, "x": 2, "y": 7}
-- RANDOM_ROWS: move_robot
-- row: {"head": null, "id": 70019, "robot_id": 2, "x": 2, "y": 11}
-- row: {"head": null, "id": 17554, "robot_id": 5, "x": 69, "y": 3}
-- row: {"head": null, "id": 116904, "robot_id": 3, "x": 0, "y": 3}
-- row: {"head": null, "id": 7184, "robot_id": 5, "x": 9, "y": 1}
-- row: {"head": null, "id": 72713, "robot_id": 5, "x": 27, "y": 11}
-- id: unique values=18031, range=3777..187064
-- robot_id: nulls=0, non_nulls=18031, distinct=8
-- robot_id numeric: min=1, median=5.0000, max=8
-- robot_id values: 5=3849, 3=3390, 7=2933, 8=2243, 6=1736, 4=1709, 1=1704, 2=467
-- x: nulls=0, non_nulls=18031, distinct=64
-- x numeric: min=0, median=18.0000, max=70
-- x top_values: 2=1625, 3=1030, 4=808, 5=723, 0=619, 8=590, 7=556, 9=501, 10=463, 12=432
-- y: nulls=0, non_nulls=18031, distinct=11
-- y numeric: min=1, median=6.0000, max=11
-- y values: 1=2563, 3=2265, 11=2092, 9=2072, 2=2067, 7=1834, 5=1750, 10=1720, 6=1661, 8=6
-- head: nulls=17967, non_nulls=64, distinct=5
-- head values: E=23, W=21, ZERO=14, S=3, N=3


CREATE TABLE `move_timings` (
  `dist_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`dist_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=5
-- ALL_ROWS: move_timings
-- row: {"dist_mm": 5, "time_s": 2.0}
-- row: {"dist_mm": 480, "time_s": 7.1}
-- row: {"dist_mm": 680, "time_s": 8.0}
-- row: {"dist_mm": 2237, "time_s": 10.0}
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
-- row: {"id": 243, "level": 0, "type": "CELL_INTERIOR", "x": 54, "y": 0}
-- row: {"id": 161, "level": 2, "type": "CELL_INTERIOR", "x": 33, "y": 0}
-- row: {"id": 495, "level": 0, "type": "CELL_INTERIOR", "x": 45, "y": 12}
-- row: {"id": 48, "level": 1, "type": "CELL_INTERIOR", "x": 5, "y": 0}
-- row: {"id": 225, "level": 2, "type": "CELL_INTERIOR", "x": 49, "y": 0}
-- id: unique values=682, range=1..682
-- x: nulls=0, non_nulls=682, distinct=72
-- x numeric: min=0, median=32.0000, max=71
-- x top_values: 0=48, 1=48, 71=34, 2=8, 3=8, 4=8, 5=8, 6=8, 7=8, 8=8
-- y: nulls=0, non_nulls=682, distinct=13
-- y numeric: min=0, median=6.0000, max=12
-- y values: 0=288, 12=288, 2=12, 6=12, 10=12, 4=10, 5=10, 7=10, 8=10, 1=9
-- type: nulls=0, non_nulls=682, distinct=1
-- type values: CELL_INTERIOR=682
-- level: nulls=0, non_nulls=682, distinct=4
-- level numeric: min=0, median=2.0000, max=3
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=1
-- ALL_ROWS: planner_params
-- row: {"a_star_max_forward_plan_time_s": 180.0, "a_star_max_n_actions_per_path": 750, "battery_full_charge": 85, "battery_low_charge": 25, "battery_medium_charge": 35, "battery_min_charge": 10, "id": 4, "mapf_n_of_robot_planning_orders_tried_per_path": 6, "max_gripper_inclination": 5.0, "max_wait_at_picking_port_s": 15.0, "n_positions_tried_at_box": 4, "n_robots_tried_for_task": 1, "port_lift_up_delta_mm": 400, "try_restacking": 1, "wait_at_picking_port_storage_task_s": 5.0}


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
-- row: {"id": 5, "ip": "192.168.127.83", "level": 0, "port": 2000, "status": "PLANNABLE"}
-- row: {"id": 6, "ip": "192.168.127.86", "level": 1, "port": 2000, "status": "OUT_OF_GRID"}
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
) ENGINE=InnoDB AUTO_INCREMENT=1187394 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=488166
-- LATEST_ROWS: robot_state_history
-- row: {"acceleration": 0, "battery_charge": 91, "box_id": 32000874, "encoder_wheel_1": "29.5850000000", "encoder_wheel_2": "33.9000000000", "encoder_wheel_3": "-34.3570000000", "encoder_wheel_4": "-32.8260000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": -1, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1187393, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.649, "timestamp": "2026-06-25T14:48:14.536000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 2, "x_mm": 1000, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 91, "box_id": 32000874, "encoder_wheel_1": "29.5850000000", "encoder_wheel_2": "33.9000000000", "encoder_wheel_3": "-34.3570000000", "encoder_wheel_4": "-32.8260000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": -1, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1187392, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.649, "timestamp": "2026-06-25T14:48:14.536000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 2, "x_mm": 1000, "y": 1, "y_mm": 200}
-- row: {"acceleration": 0, "battery_charge": 91, "box_id": 32000874, "encoder_wheel_1": "29.5850000000", "encoder_wheel_2": "33.9000000000", "encoder_wheel_3": "-34.3570000000", "encoder_wheel_4": "-32.8260000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": -1, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1187391, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 7, "speed": 0, "steering_encoder_deg": 89.649, "timestamp": "2026-06-25T14:48:14.536000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 2, "x_mm": 1000, "y": 1, "y_mm": 200}
-- RANDOM_ROWS: robot_state_history
-- row: {"acceleration": 0, "battery_charge": 69, "box_id": 32000876, "encoder_wheel_1": "2917.3830000000", "encoder_wheel_2": "-1045.3230000000", "encoder_wheel_3": "2837.8760000000", "encoder_wheel_4": "-2933.6980000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 21, "gripper_state": "UNCL", "head_rotation_deg": 1, "head_state": "E", "id": 938980, "level": 0, "lift_mm": 1410, "lift_state": "MID", "pos_sensors": 31, "ready_for_next_command": "EXEC", "robot_id": 5, "speed": 0, "steering_encoder_deg": 91.725, "timestamp": "2026-04-20T17:10:44.230000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 4, "x_mm": 1960, "y": 2, "y_mm": 880}
-- row: {"acceleration": 0, "battery_charge": 59, "box_id": 32001072, "encoder_wheel_1": "12754.4670000000", "encoder_wheel_2": "17168.0620000000", "encoder_wheel_3": "-17176.2650000000", "encoder_wheel_4": "-12754.8170000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 1, "gripper_acc_y": -2, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": 1, "head_state": "E", "id": 1160546, "level": 0, "lift_mm": 5, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 5, "speed": 0, "steering_encoder_deg": 91.803, "timestamp": "2026-06-17T07:05:55.545000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 40, "x_mm": 16860, "y": 5, "y_mm": 2437}
-- row: {"acceleration": 0, "battery_charge": 41, "box_id": 32000552, "encoder_wheel_1": "20243.4050000000", "encoder_wheel_2": "22939.9020000000", "encoder_wheel_3": "-22955.5420000000", "encoder_wheel_4": "-20238.9910000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 1, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 9, "gripper_state": "EMPT", "head_rotation_deg": 1, "head_state": "E", "id": 1142989, "level": 0, "lift_mm": 0, "lift_state": "TOP", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 5, "speed": 0, "steering_encoder_deg": 91.79, "timestamp": "2026-06-11T13:33:19.286000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 54, "x_mm": 22560, "y": 3, "y_mm": 1560}
-- row: {"acceleration": 0, "battery_charge": 75, "box_id": 32000247, "encoder_wheel_1": "-8797.1680000000", "encoder_wheel_2": "-7043.1940000000", "encoder_wheel_3": "7291.6300000000", "encoder_wheel_4": "8795.8460000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": 0, "gripper_acc_y": 0, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 21, "gripper_state": "UNCL", "head_rotation_deg": 1, "head_state": "E", "id": 905544, "level": 0, "lift_mm": 1410, "lift_state": "MID", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 5, "speed": 0, "steering_encoder_deg": 91.792, "timestamp": "2026-04-16T09:43:28.822000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 8, "x_mm": 3540, "y": 2, "y_mm": 880}
-- row: {"acceleration": 0, "battery_charge": 78, "box_id": 32002154, "encoder_wheel_1": "7922.9160000000", "encoder_wheel_2": "-3774.7440000000", "encoder_wheel_3": "3788.3190000000", "encoder_wheel_4": "-7917.2230000000", "error_id0": 0, "error_id1": 0, "error_id2": 0, "error_id3": 0, "error_id4": 0, "error_id5": 0, "error_id6": 0, "error_id7": 0, "error_id8": 0, "error_id9": 0, "gripper_acc_x": -6, "gripper_acc_y": -6, "gripper_extension_mm": 0, "gripper_extension_state": "MID", "gripper_sensors": 7, "gripper_state": "FULL", "head_rotation_deg": -1, "head_state": "E", "id": 988663, "level": 1, "lift_mm": 475, "lift_state": "MID", "pos_sensors": 31, "ready_for_next_command": "READY", "robot_id": 6, "speed": 0, "steering_encoder_deg": 91.595, "timestamp": "2026-05-06T09:39:42.863000", "wheel_drives": "WELL", "wheels_direction": "X", "x": 7, "x_mm": 3060, "y": 1, "y_mm": 200}
-- id: unique values=488166, range=699228..1187393
-- robot_id: nulls=0, non_nulls=488166, distinct=7
-- robot_id numeric: min=1, median=6.0000, max=8
-- robot_id values: 5=165227, 7=157973, 6=57092, 8=46578, 3=26770, 1=21247, 4=13279
-- timestamp: nulls=0, non_nulls=488166, distinct=275444
-- timestamp top_values: 2026-06-08 13:26:13.568000=12, 2026-04-08 10:14:24.206000=11, 2026-04-08 10:34:07.275000=11, 2026-04-09 08:07:29.947000=11, 2026-04-09 10:21:48.805000=11, 2026-04-09 13:52:17.099000=11, 2026-04-10 06:50:24.187000=11, 2026-04-14 10:23:56.905000=11, 2026-04-14 13:02:24.752000=11, 2026-04-15 06:14:53.363000=11
-- ready_for_next_command: nulls=0, non_nulls=488166, distinct=5
-- ready_for_next_command values: READY=302621, EXEC=119336, ALARM=65785, N_RDY=392, N_CON=32
-- battery_charge: nulls=0, non_nulls=488166, distinct=88
-- battery_charge numeric: min=0, median=70.0000, max=100
-- battery_charge top_values: 46=14875, 78=13935, 76=12036, 89=11965, 64=11642, 84=11529, 48=11428, 47=11413, 77=10218, 63=10153
-- lift_state: nulls=0, non_nulls=488166, distinct=5
-- lift_state values: TOP=331998, MID=147184, RUN=8912, CLBR=59, ZERO=13
-- lift_mm: nulls=0, non_nulls=488166, distinct=1995
-- lift_mm numeric: min=-224, median=2.0000, max=4980
-- lift_mm top_values: 0=207434, 1=20549, 7=19901, 6=19271, 2=18202, 5=17993, 2060=16039, 4=14314, 3=9672, 1750=9216
-- gripper_state: nulls=0, non_nulls=488166, distinct=5
-- gripper_state values: FULL=235738, EMPT=208402, UNCL=36177, RUN=7836, ZERO=13
-- wheels_direction: nulls=0, non_nulls=488166, distinct=5
-- wheels_direction values: X=296618, Y=187345, ZERO=2364, RUN=1387, CLBR=452
-- wheel_drives: nulls=0, non_nulls=488166, distinct=5
-- wheel_drives values: WELL=458782, LOST=13493, ROUGH=8237, RUN=7538, CLBR=116
-- x: nulls=0, non_nulls=488166, distinct=57
-- x numeric: min=0, median=27.0000, max=70
-- x top_values: 2=54732, 70=37339, 4=26700, 3=18132, 7=18132, 12=16935, 13=15450, 68=15392, 8=12742, 9=12279
-- y: nulls=0, non_nulls=488166, distinct=11
-- y numeric: min=0, median=3.0000, max=42
-- y values: 1=148057, 11=59738, 3=55268, 2=54735, 5=51742, 9=45140, 10=28974, 6=23676, 7=20814, 0=17
-- level: nulls=0, non_nulls=488166, distinct=4
-- level numeric: min=0, median=0.0000, max=3
-- level values: 0=323208, 1=103666, 2=34524, 3=26768
-- head_state: nulls=0, non_nulls=488166, distinct=2
-- head_state values: E=487947, ZERO=219
-- gripper_extension_state: nulls=0, non_nulls=488166, distinct=4
-- gripper_extension_state values: MID=487555, RUN=559, CLBR=39, ZERO=13
-- head_rotation_deg: nulls=0, non_nulls=488166, distinct=5
-- head_rotation_deg numeric: min=-3, median=1.0000, max=1
-- head_rotation_deg values: 1=249167, 0=150371, -1=87560, -2=888, -3=180
-- gripper_extension_mm: nulls=0, non_nulls=488166, distinct=84
-- gripper_extension_mm numeric: min=-122, median=0.0000, max=206
-- gripper_extension_mm top_values: 0=445376, 140=17792, 196=11992, 86=5297, 106=2771, -1=1294, 200=987, 97=965, 2=478, 7=346
-- error_id0: nulls=0, non_nulls=488166, distinct=1
-- error_id0 numeric: min=0, median=0.0000, max=0
-- error_id0 values: 0=488166
-- error_id1: nulls=0, non_nulls=488166, distinct=4
-- error_id1 numeric: min=0, median=0.0000, max=1001
-- error_id1 values: 0=488120, 1001=39, 11=6, 1=1
-- error_id2: nulls=0, non_nulls=488166, distinct=13
-- error_id2 numeric: min=0, median=0.0000, max=1014
-- error_id2 values: 0=473900, 1010=7732, 1014=2208, 1008=2194, 1009=939, 1012=378, 1013=361, 1=243, 1007=109, 1001=59
-- error_id3: nulls=0, non_nulls=488166, distinct=5
-- error_id3 numeric: min=0, median=0.0000, max=1008
-- error_id3 values: 0=487332, 1001=446, 1008=353, 1007=32, 19=3
-- error_id4: nulls=0, non_nulls=488166, distinct=10
-- error_id4 numeric: min=0, median=0.0000, max=1015
-- error_id4 values: 0=472312, 1012=13941, 18=1128, 1005=375, 1003=305, 11=64, 1=19, 1015=16, 1002=5, 4=1
-- error_id5: nulls=0, non_nulls=488166, distinct=2
-- error_id5 numeric: min=0, median=0.0000, max=27
-- error_id5 values: 0=487539, 27=627
-- error_id6: nulls=0, non_nulls=488166, distinct=5
-- error_id6 numeric: min=0, median=0.0000, max=8
-- error_id6 values: 0=452564, 8=18158, 4=9851, 1=7357, 3=236
-- error_id7: nulls=0, non_nulls=488166, distinct=1
-- error_id7 numeric: min=0, median=0.0000, max=0
-- error_id7 values: 0=488166
-- error_id8: nulls=0, non_nulls=488166, distinct=6
-- error_id8 numeric: min=0, median=0.0000, max=16
-- error_id8 values: 0=487858, 13=108, 4=96, 7=57, 1=46, 16=1
-- error_id9: nulls=0, non_nulls=488166, distinct=20
-- error_id9 numeric: min=0, median=0.0000, max=11104
-- error_id9 top_values: 0=486734, 6001=924, 11104=216, 5211=45, 5216=37, 11102=36, 5212=35, 5208=30, 10204=26, 10215=22
-- speed: nulls=0, non_nulls=488166, distinct=395
-- speed numeric: min=-1500, median=0.0000, max=1500
-- speed top_values: 0=481280, -20=1519, 20=1316, 25=341, -10=219, 10=160, -40=129, 12=118, -12=110, 40=108
-- acceleration: nulls=0, non_nulls=488166, distinct=399
-- acceleration numeric: min=-705, median=0.0000, max=686
-- acceleration top_values: 0=484632, 8=820, -8=454, -40=135, -20=132, 40=128, 80=39, 20=37, 10=27, -80=26
-- box_id: nulls=47084, non_nulls=441082, distinct=555
-- box_id numeric: min=17000025, median=32000552.0000, max=32005990
-- box_id top_values: 32002137=10543, 32000854=9639, 32000552=6459, 32000818=5950, 32000258=5750, 32000489=4982, 32000423=4746, 32000544=4682, 32000040=4637, 32002107=4560
-- encoder_wheel_1: nulls=0, non_nulls=488166, distinct=140416
-- encoder_wheel_1 numeric: min=-29796.7730000000, median=7588.51, max=34273.6480000000
-- encoder_wheel_1 top_values: 6041.8210000000=4251, 6041.8220000000=4086, 5907.8080000000=3021, 5907.8090000000=2190, -3177.3510000000=2173, 14246.4100000000=2055, 5868.5160000000=1679, 7020.0660000000=1492, 465.6130000000=1384, 4396.0660000000=1348
-- encoder_wheel_2: nulls=0, non_nulls=488166, distinct=139208
-- encoder_wheel_2 numeric: min=-26318.9080000000, median=9025.37, max=35022.8810000000
-- encoder_wheel_2 top_values: -5889.7870000000=5833, 17703.4840000000=4258, -3125.0360000000=2302, -5825.2450000000=2236, 19109.9550000000=2209, 516.2860000000=1970, 18852.8470000000=1848, -5889.7880000000=1637, 4673.4100000000=1536, -5889.7860000000=1511
-- encoder_wheel_3: nulls=0, non_nulls=488166, distinct=139169
-- encoder_wheel_3 numeric: min=-34836.4820000000, median=-8791.02, max=26320.6190000000
-- encoder_wheel_3 top_values: 4399.3380000000=3840, -17717.5980000000=3765, 4399.3390000000=3095, -18823.6180000000=2885, 3116.1050000000=2028, -4598.4380000000=1843, 3116.1040000000=1494, -16309.7570000000=1379, 5705.8170000000=1344, -525.0170000000=1314
-- encoder_wheel_4: nulls=0, non_nulls=488166, distinct=142003
-- encoder_wheel_4 numeric: min=-34489.4210000000, median=-7836.5, max=29783.6000000000
-- encoder_wheel_4 top_values: -5946.6940000000=5609, -5922.1830000000=4033, -5946.6950000000=2818, -5852.0080000000=2146, -14277.2110000000=2141, -4466.8100000000=1983, -7032.9310000000=1717, 3178.5460000000=1605, -464.8140000000=1553, -5018.8150000000=1455
-- pos_sensors: nulls=0, non_nulls=488166, distinct=28
-- pos_sensors numeric: min=0, median=31.0000, max=31
-- pos_sensors top_values: 31=391301, 30=24270, 23=23561, 29=15937, 12=10897, 14=5037, 15=5025, 27=4081, 3=2970, 13=1602
-- gripper_acc_x: nulls=0, non_nulls=488166, distinct=63
-- gripper_acc_x numeric: min=-55, median=0.0000, max=67
-- gripper_acc_x top_values: 0=303455, 1=132779, -1=35033, 2=6066, -2=3013, -6=1733, 3=1312, 4=955, -3=639, 12=590
-- gripper_acc_y: nulls=0, non_nulls=488166, distinct=66
-- gripper_acc_y numeric: min=-68, median=0.0000, max=70
-- gripper_acc_y top_values: 0=238057, -1=197083, -2=28111, 1=8425, -3=3199, 2=2707, -4=2613, 6=2197, -6=1356, 3=1219
-- gripper_sensors: nulls=0, non_nulls=488166, distinct=21
-- gripper_sensors numeric: min=0, median=9.0000, max=23
-- gripper_sensors top_values: 9=204517, 7=146891, 13=68880, 21=35541, 3=10583, 12=5698, 5=4238, 8=3855, 4=3230, 6=3115
-- x_mm: nulls=0, non_nulls=488166, distinct=2953
-- x_mm numeric: min=-2295, median=11300.0000, max=29270
-- x_mm top_values: 1000=42358, 29220=36562, 1960=25450, 3060=17371, 1480=17111, 5120=16607, 5600=15074, 28260=13644, 3540=12243, 4020=11696
-- y_mm: nulls=0, non_nulls=488166, distinct=902
-- y_mm numeric: min=-400, median=1560.0000, max=6114
-- y_mm top_values: 200=137085, 6034=58129, 880=53650, 1560=52182, 2437=49488, 4674=42906, 5354=28079, 3117=20142, 3797=19766, 199=4446
-- steering_encoder_deg: nulls=0, non_nulls=488166, distinct=3194
-- steering_encoder_deg numeric: min=-0.696, median=89.68, max=92.955
-- steering_encoder_deg top_values: 91.593=9129, 91.808=7782, 91.831=6038, 0.337=5729, 89.691=4417, 89.693=4223, 0.092=3554, 0.084=3535, 91.827=3471, 91.602=3468


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
) ENGINE=InnoDB AUTO_INCREMENT=24862 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=7685
-- LATEST_ROWS: safety_events
-- row: {"box_id": 32000874, "check_name": "StartStateCheck", "command_id": "ACK_ERROR", "finished_tick": 1521, "id": 24861, "json_data": "{'command_id': 'ACK_ERROR', 'param1': 0, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': 0, 'start_tick': 1521, 'finished_tick': 1521, 'start_state': {'robot_id': 7, 'timestamp': '2026-06-25T15:48:11.303477Z', 'ready_for_next_command': 4, 'battery_charge': 91, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000874, 'encoder_wheel_1': 29.586000000000002, 'encoder_wheel_2': 33.903, 'encoder_wheel_3': -34.361000000000004, 'encoder_wheel_4': -32.855000000000004, 'steering_encoder_deg': 89.649, 'pos_sensors': 15, 'gripper_acc_x': -1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 1003, 'y_mm': 199}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-06-25T15:48:11.303477Z', 'ready_for_next_command': 2, 'battery_charge': 91, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000874, 'encoder_wheel_1': 29.586000000000002, 'encoder_wheel_2': 33.903, 'encoder_wheel_3': -34.361000000000004, 'encoder_wheel_4': -32.855000000000004, 'steering_encoder_deg': 89.649, 'pos_sensors': 15, 'gripper_acc_x': -1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 1003, 'y_mm': 199}, 'expected_duration_s': 1.0, 'task_id': 187068, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :ALARM  2 1  0 steer=X head=E(1  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000874 whls=LOST pos=1111 grip=1001 errs=(4, 1012) 91%\nRecvd:7 :ALARM  2 1  0 steer=X head=E(1  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000874 pos=11111 grip=1001 errs=(4, 1012) 91%", "param1": 0, "robot_id": 7, "start_tick": 1521, "task_id": 187068, "tick": 1521, "time": "2026-06-25T14:48:11"}
-- row: {"box_id": null, "check_name": "StartStateCheck", "command_id": "PUT_BOX", "finished_tick": 112, "id": 24860, "json_data": "{'command_id': 'PUT_BOX', 'param1': 3, 'param2': 0, 'param3': 0, 'param4': 100, 'box_id': 32000798, 'dist_mm': 0, 'start_tick': 112, 'finished_tick': 112, 'start_state': {'robot_id': 7, 'timestamp': '2026-06-25T15:33:56.184109Z', 'ready_for_next_command': 2, 'battery_charge': 92, 'lift_state': 1, 'lift_mm': 3, 'gripper_state': 2, 'wheels_direction': 2, 'x': 60, 'y': 10, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 18915.854, 'encoder_wheel_2': 29228.516, 'encoder_wheel_3': -29229.062, 'encoder_wheel_4': -18918.778000000002, 'steering_encoder_deg': 0.276, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 25100, 'y_mm': 5354}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-06-25T15:33:56.184109Z', 'ready_for_next_command': 2, 'battery_charge': 92, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 60, 'y': 10, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 18915.854, 'encoder_wheel_2': 29228.516, 'encoder_wheel_3': -29229.062, 'encoder_wheel_4': -18918.778000000002, 'steering_encoder_deg': 0.276, 'pos_sensors': 31, 'gripper_acc_x': -1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 25100, 'y_mm': 5354}, 'expected_duration_s': 0.5065565808644973, 'task_id': 187043, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :READY 60 10 0 steer=Y head=E(1  ) lift=TOP(    3mm) grip=EMPT MID  0   no box pos=11111 grip=1001  92%\nRecvd:7 :EXEC  60 10 0 steer=Y head=E(1  ) lift=TOP(    3mm) grip=EMPT MID  0   no box pos=11111 grip=1001  92%", "param1": 3, "robot_id": 7, "start_tick": 112, "task_id": 187043, "tick": 112, "time": "2026-06-25T14:33:57"}
-- row: {"box_id": 32000557, "check_name": "StartStateCheck", "command_id": "ACK_ERROR", "finished_tick": 579, "id": 24859, "json_data": "{'command_id': 'ACK_ERROR', 'param1': 0, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': 0, 'start_tick': 579, 'finished_tick': 579, 'start_state': {'robot_id': 7, 'timestamp': '2026-06-25T09:08:55.269908Z', 'ready_for_next_command': 3, 'battery_charge': 46, 'lift_state': 1, 'lift_mm': 6, 'gripper_state': 1, 'wheels_direction': 10, 'x': 19, 'y': 5, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000557, 'encoder_wheel_1': 2847.219, 'encoder_wheel_2': 7341.851000000001, 'encoder_wheel_3': -7340.494000000001, 'encoder_wheel_4': -2858.212, 'steering_encoder_deg': 70.278, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 7, 'x_mm': 8139, 'y_mm': 2436}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-06-25T09:08:55.269908Z', 'ready_for_next_command': 2, 'battery_charge': 46, 'lift_state': 1, 'lift_mm': 6, 'gripper_state': 1, 'wheels_direction': 10, 'x': 19, 'y': 5, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000557, 'encoder_wheel_1': 2847.219, 'encoder_wheel_2': 7341.851000000001, 'encoder_wheel_3': -7340.494000000001, 'encoder_wheel_4': -2858.212, 'steering_encoder_deg': 70.278, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 7, 'x_mm': 8139, 'y_mm': 2436}, 'expected_duration_s': 1.0, 'task_id': 187005, 'status': 'NEW', 'action_history_id': None}", "message": "Planned start state is different from actual recieved state:\nStart:7 :EXEC  19 5  0 steer=RUN head=E(1  ) lift=TOP(    6mm) grip=FULL MID  0   box=32000557 pos=11111 grip=111  46%\nRecvd:7 :READY 19 5  0 steer=X head=E(1  ) lift=TOP(    6mm) grip=FULL MID  0   box=32000557 pos=11111 grip=111  46%", "param1": 0, "robot_id": 7, "start_tick": 579, "task_id": 187005, "tick": 579, "time": "2026-06-25T08:08:56"}
-- RANDOM_ROWS: safety_events
-- row: {"box_id": null, "check_name": "MoveWithLoweredLiftCheck", "command_id": "MOVE", "finished_tick": 148, "id": 17202, "json_data": "{'command_id': 'MOVE', 'param1': -1, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': -680, 'start_tick': 144, 'finished_tick': 148, 'start_state': {'robot_id': 5, 'timestamp': '2026-03-10T13:46:10.280986Z', 'ready_for_next_command': 4, 'battery_charge': 52, 'lift_state': 2, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 53, 'y': 2, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 1014, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 19939.546000000002, 'encoder_wheel_2': 21303.392, 'encoder_wheel_3': -21297.653000000002, 'encoder_wheel_4': -19939.193, 'steering_encoder_deg': -0.016, 'pos_sensors': 23, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 22080, 'y_mm': 880}, 'finish_state': {'robot_id': 5, 'timestamp': '2026-03-10T13:46:13.280986Z', 'ready_for_next_command': 4, 'battery_charge': 52, 'lift_state': 2, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 53, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 1014, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 19939.546000000002, 'encoder_wheel_2': 21303.392, 'encoder_wheel_3': -21297.653000000002, 'encoder_wheel_4': -19939.193, 'steering_encoder_deg': -0.016, 'pos_sensors': 23, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 22080, 'y_mm': 880}, 'expected_duration_s': 3.0, 'task_id': 155313, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "Robot is trying to move with lift state MID", "param1": -1, "robot_id": 5, "start_tick": 144, "task_id": 155313, "tick": 144, "time": "2026-03-10T12:46:10"}
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 3904, "id": 19885, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 3903, 'finished_tick': 3904, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:10:26.981772Z', 'ready_for_next_command': 4, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.603, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.251, 'encoder_wheel_4': -2643.495, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:10:26.981772Z', 'ready_for_next_command': 2, 'battery_charge': 64, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.603, 'encoder_wheel_2': -3265.6330000000003, 'encoder_wheel_3': 3356.251, 'encoder_wheel_4': -2643.495, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 64%", "param1": 1005, "robot_id": 6, "start_tick": 3903, "task_id": 164688, "tick": 3903, "time": "2026-03-20T09:10:27"}
-- row: {"box_id": null, "check_name": "InterrobotCollisionsChecker", "command_id": "RECOVER", "finished_tick": 95, "id": 17479, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': 72, 'param3': 40, 'box_id': None, 'dist_mm': 72, 'start_tick': 93, 'finished_tick': 95, 'start_state': {'robot_id': 1, 'timestamp': '2026-03-12T08:18:18.632874Z', 'ready_for_next_command': 4, 'battery_charge': 98, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 7, 'level': 2, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -3676.261, 'encoder_wheel_2': 3521.483, 'encoder_wheel_3': -3192.919, 'encoder_wheel_4': 3605.121, 'steering_encoder_deg': 0.323, 'pos_sensors': 3, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 1000, 'y_mm': 3747}, 'finish_state': {'robot_id': 1, 'timestamp': '2026-03-12T08:18:18.632874Z', 'ready_for_next_command': 2, 'battery_charge': 98, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 7, 'level': 2, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -3676.261, 'encoder_wheel_2': 3521.483, 'encoder_wheel_3': -3192.919, 'encoder_wheel_4': 3605.121, 'steering_encoder_deg': 0.323, 'pos_sensors': 3, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 1000, 'y_mm': 3747}, 'expected_duration_s': 1.8, 'task_id': 157765, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "IRC: Robot 1 is colliding with another robot for action NEW|  93:95  |T157765|Robot 1 RECOVER move 72mm 40mm/s || 1 :ALARM  2 7  2 steer=Y head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   no box whls=LOST pos=11 grip=1001(4, 1012) 98%", "param1": 1005, "robot_id": 1, "start_tick": 93, "task_id": 157765, "tick": 93, "time": "2026-03-12T07:18:19"}
-- row: {"box_id": null, "check_name": "InterrobotCollisionsChecker", "command_id": "LIFT", "finished_tick": 2683, "id": 17999, "json_data": "{'command_id': 'LIFT', 'param1': 0, 'param2': 0, 'param3': 0, 'box_id': 32000673, 'dist_mm': 0, 'start_tick': 2667, 'finished_tick': 2683, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-17T16:28:22.886902Z', 'ready_for_next_command': 2, 'battery_charge': 81, 'lift_state': 2, 'lift_mm': 1595, 'gripper_state': 1, 'wheels_direction': 1, 'x': 32, 'y': 2, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000673, 'encoder_wheel_1': 25376.909, 'encoder_wheel_2': 17808.152000000002, 'encoder_wheel_3': -17835.794, 'encoder_wheel_4': -25383.342, 'steering_encoder_deg': 0.34, 'pos_sensors': 23, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 21, 'x_mm': 22560, 'y_mm': 1560}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-17T16:28:22.886902Z', 'ready_for_next_command': 2, 'battery_charge': 81, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 32, 'y': 2, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000673, 'encoder_wheel_1': 25376.909, 'encoder_wheel_2': 17808.152000000002, 'encoder_wheel_3': -17835.794, 'encoder_wheel_4': -25383.342, 'steering_encoder_deg': 0.34, 'pos_sensors': 23, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 21, 'x_mm': 22560, 'y_mm': 1560}, 'expected_duration_s': 9.723064516129032, 'task_id': 163156, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "IRC: Robot 6 is colliding with another robot for action NEW|2667:2683|T163156|Robot 6 LIFT 0                || 6 :READY 32 2  1 steer=X head=E(0  ) lift=MID( 1595mm) grip=FULL MID  0   box=32000673 pos=10111 grip=10101 81%", "param1": 0, "robot_id": 6, "start_tick": 2667, "task_id": 163156, "tick": 2616, "time": "2026-03-17T15:28:05"}
-- row: {"box_id": 32000777, "check_name": "CMDConstraintsCheck", "command_id": "RECOVER", "finished_tick": 5128, "id": 21109, "json_data": "{'command_id': 'RECOVER', 'param1': 1005, 'param2': -36, 'param3': 40, 'box_id': None, 'dist_mm': -36, 'start_tick': 5127, 'finished_tick': 5128, 'start_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:44:11.203719Z', 'ready_for_next_command': 4, 'battery_charge': 63, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 0, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.253, 'encoder_wheel_4': -2643.494, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-03-20T10:44:11.203719Z', 'ready_for_next_command': 2, 'battery_charge': 63, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 1, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 1012, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000777, 'encoder_wheel_1': 2551.602, 'encoder_wheel_2': -3265.632, 'encoder_wheel_3': 3356.253, 'encoder_wheel_4': -2643.494, 'steering_encoder_deg': 91.724, 'pos_sensors': 12, 'gripper_acc_x': 0, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 487, 'y_mm': 1559}, 'expected_duration_s': 0.9, 'task_id': 164688, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}", "message": "state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 63%", "param1": 1005, "robot_id": 6, "start_tick": 5127, "task_id": 164688, "tick": 5127, "time": "2026-03-20T09:44:11"}
-- id: unique values=7685, range=17177..24861
-- check_name: nulls=0, non_nulls=7685, distinct=7
-- check_name values: CMDConstraintsCheck=3343, InterrobotCollisionsChecker=2960, StartStateCheck=915, MoveWithLoweredLiftCheck=398, LiftSafetyChecker=59, LiftDownToInactivePort=7, MoveOutboundCheck=3
-- message: nulls=0, non_nulls=7685, distinct=2320
-- message top_values: state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 64%=955, state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 63%=953, state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 65%=910, IRC: Robot 7 is colliding with another robot for action NEW| 354:356 |T177950|Robot 7 RECOVER move 36mm 20mm/s || 7 :ALARM 32 10 0 steer=X head=E(1  ) lift=TOP(    0mm) grip=FULL MID  0   box=32000540 whls=LOST pos=1100 grip=111(4, 1012) 62%=417, state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=32000777 pos=1100 grip=1001(4, 1012) 62%=304, IRC: Standing robot 7, 5:1:0 is colliding with another standing robot=245, Robot is trying to move with lift height -224mm=153, Robot is trying to move with lift state MID=150, state constraint violated: CMDConstraint(id=19, x=1, y=3, level=1, head=None, wheel=None, command=None, param1=None) for finished state 6 :READY  1 3  1 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   box=17000063 pos=1100 grip=1001(4, 1012) 34%=122, IRC: Robot 5 is colliding with another robot for action NEW|   1:21  |T183387|Robot 5 MOVE to X=42 Y=5 5220mm || 5 :READY 29 5  0 steer=X head=E(0  ) lift=TOP(    0mm) grip=EMPT MID  0   no box pos=11111 grip=1001  46%=105
-- message shape: letters+digits=9
-- tick: nulls=0, non_nulls=7685, distinct=3959
-- tick numeric: min=1, median=1855.0000, max=12592
-- tick top_values: 1=467, 354=436, 7090=249, 2327=132, 315=102, 61=88, 74=76, 98=65, 3=58, 5=36
-- time: nulls=0, non_nulls=7685, distinct=6460
-- time top_values: 2026-03-18 10:07:01=14, 2026-03-18 10:07:22=14, 2026-03-18 10:08:04=14, 2026-03-18 10:08:25=14, 2026-03-18 10:08:46=14, 2026-05-19 08:46:02=12, 2026-05-19 08:46:07=12, 2026-05-19 08:46:09=12, 2026-03-18 10:35:46=10, 2026-05-20 08:58:39=10
-- robot_id: nulls=0, non_nulls=7685, distinct=7
-- robot_id numeric: min=1, median=6.0000, max=8
-- robot_id values: 6=3672, 7=1774, 5=1541, 1=387, 8=268, 3=27, 4=16
-- task_id: nulls=256, non_nulls=7429, distinct=706
-- task_id numeric: min=155269, median=164688.0000, max=187068
-- task_id top_values: 164688=3122, 183387=450, 177950=435, 185707=288, 157765=224, 155892=163, 163156=160, 165448=122, 158245=104, 172395=100
-- box_id: nulls=3656, non_nulls=4029, distinct=208
-- box_id numeric: min=17000047, median=32000777.0000, max=32002154
-- box_id top_values: 32000777=3135, 17000063=122, 32000859=91, 32000858=47, 32000809=43, 32000281=35, 32000812=27, 32000552=23, 32000258=22, 32000851=19
-- command_id: nulls=0, non_nulls=7685, distinct=12
-- command_id values: RECOVER=4533, MOVE=1379, IDLE=441, LIFT=400, TAKE_BOX=245, ROTATE_WHEELS=227, STOP=157, PUT_BOX=125, EXTEND_GRIPPER=87, ACK_ERROR=42
-- param1: nulls=0, non_nulls=7685, distinct=110
-- param1 numeric: min=-68, median=1005.0000, max=4688
-- param1 top_values: 1005=4486, 0=466, 2=323, 1000=256, 5=231, 1=155, 13=151, -39=150, 1430=150, -1=126
-- start_tick: nulls=0, non_nulls=7685, distinct=4169
-- start_tick numeric: min=1, median=1890.0000, max=12592
-- start_tick top_values: 354=437, 1=253, 7090=249, 37=123, 22=119, 315=103, 61=90, 74=83, 98=69, 2327=43
-- finished_tick: nulls=0, non_nulls=7685, distinct=4181
-- finished_tick numeric: min=2, median=1905.0000, max=12594
-- finished_tick top_values: 356=429, 8090=245, 73=116, 21=113, 36=109, 3=100, 63=92, 317=91, 88=81, 139=64
-- json_data: nulls=0, non_nulls=7685, distinct=7415
-- json_data top_values: {}=256, {'command_id': 'MOVE', 'param1': -2, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': -877, 'start_tick': 631, 'finished_tick': 635, 'start_state': {'robot_id': 5, 'timestamp': '2026-04-09T09:31:43.128677Z', 'ready_for_next_command': 2, 'battery_charge': 85, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 9, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -5372.7, 'encoder_wheel_2': 3629.744, 'encoder_wheel_3': -3595.911, 'encoder_wheel_4': 5350.331, 'steering_encoder_deg': 91.778, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 0, 'y_mm': 4674}, 'finish_state': {'robot_id': 5, 'timestamp': '2026-04-09T09:31:46.128677Z', 'ready_for_next_command': 2, 'battery_charge': 85, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 7, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -5372.7, 'encoder_wheel_2': 3629.744, 'encoder_wheel_3': -3595.911, 'encoder_wheel_4': 5350.331, 'steering_encoder_deg': 91.778, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 0, 'y_mm': 4674}, 'expected_duration_s': 3.0, 'task_id': 168157, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': -3, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': -1440, 'start_tick': 161, 'finished_tick': 167, 'start_state': {'robot_id': 8, 'timestamp': '2026-05-05T15:29:29.953766Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 5, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1442.765, 'encoder_wheel_2': 1441.8120000000001, 'encoder_wheel_3': -1441.407, 'encoder_wheel_4': -1442.1970000000001, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'finish_state': {'robot_id': 8, 'timestamp': '2026-05-05T15:29:34.153766Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1442.765, 'encoder_wheel_2': 1441.8120000000001, 'encoder_wheel_3': -1441.407, 'encoder_wheel_4': -1442.1970000000001, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'expected_duration_s': 4.2, 'task_id': 172693, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': -3, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': -1440, 'start_tick': 294, 'finished_tick': 300, 'start_state': {'robot_id': 8, 'timestamp': '2026-05-06T15:56:46.074434Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 5, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1442.347, 'encoder_wheel_2': 1441.372, 'encoder_wheel_3': -1440.826, 'encoder_wheel_4': -1441.772, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'finish_state': {'robot_id': 8, 'timestamp': '2026-05-06T15:56:50.274434Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1442.347, 'encoder_wheel_2': 1441.372, 'encoder_wheel_3': -1440.826, 'encoder_wheel_4': -1441.772, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'expected_duration_s': 4.2, 'task_id': 172693, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': -3, 'param2': 0, 'param3': 0, 'param4': 0, 'box_id': None, 'dist_mm': -1440, 'start_tick': 3, 'finished_tick': 9, 'start_state': {'robot_id': 8, 'timestamp': '2026-05-05T15:35:46.426217Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 5, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1441.999, 'encoder_wheel_2': 1441.019, 'encoder_wheel_3': -1440.491, 'encoder_wheel_4': -1441.417, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'finish_state': {'robot_id': 8, 'timestamp': '2026-05-05T15:35:50.626217Z', 'ready_for_next_command': 2, 'battery_charge': 77, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 9, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 1441.999, 'encoder_wheel_2': 1441.019, 'encoder_wheel_3': -1440.491, 'encoder_wheel_4': -1441.417, 'steering_encoder_deg': 88.627, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 4674}, 'expected_duration_s': 4.2, 'task_id': 172693, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': -6, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': -3597, 'start_tick': 27, 'finished_tick': 37, 'start_state': {'robot_id': 5, 'timestamp': '2026-04-08T13:30:05.055370Z', 'ready_for_next_command': 2, 'battery_charge': 98, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 7, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -2048.913, 'encoder_wheel_2': 5197.386, 'encoder_wheel_3': -5161.994, 'encoder_wheel_4': 2026.51, 'steering_encoder_deg': 91.786, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 3797}, 'finish_state': {'robot_id': 5, 'timestamp': '2026-04-08T13:30:11.655370Z', 'ready_for_next_command': 2, 'battery_charge': 98, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 2, 'x': 2, 'y': 1, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': -2048.913, 'encoder_wheel_2': 5197.386, 'encoder_wheel_3': -5161.994, 'encoder_wheel_4': 2026.51, 'steering_encoder_deg': 91.786, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 2440, 'y_mm': 3797}, 'expected_duration_s': 6.6, 'task_id': 167455, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': -68, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': -28220, 'start_tick': 87, 'finished_tick': 137, 'start_state': {'robot_id': 3, 'timestamp': '2026-04-04T11:29:47.284697Z', 'ready_for_next_command': 2, 'battery_charge': 46, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 70, 'y': 11, 'level': 3, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 28431.015, 'encoder_wheel_2': 28379.795000000002, 'encoder_wheel_3': -28376.523, 'encoder_wheel_4': -28428.399, 'steering_encoder_deg': 91.43900000000001, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 29220, 'y_mm': 6034}, 'finish_state': {'robot_id': 3, 'timestamp': '2026-04-04T11:30:17.884697Z', 'ready_for_next_command': 2, 'battery_charge': 46, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 2, 'y': 11, 'level': 3, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 28431.015, 'encoder_wheel_2': 28379.795000000002, 'encoder_wheel_3': -28376.523, 'encoder_wheel_4': -28428.399, 'steering_encoder_deg': 91.43900000000001, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 29220, 'y_mm': 6034}, 'expected_duration_s': 30.599999999999998, 'task_id': 166460, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': 2, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': 1000, 'start_tick': 92, 'finished_tick': 97, 'start_state': {'robot_id': 6, 'timestamp': '2026-04-10T07:45:52.287103Z', 'ready_for_next_command': 2, 'battery_charge': 95, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 0, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002154, 'encoder_wheel_1': 3618.841, 'encoder_wheel_2': -5345.805, 'encoder_wheel_3': 5207.461, 'encoder_wheel_4': -3892.431, 'steering_encoder_deg': 91.708, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 7, 'x_mm': 0, 'y_mm': 1560}, 'finish_state': {'robot_id': 6, 'timestamp': '2026-04-10T07:45:55.887103Z', 'ready_for_next_command': 2, 'battery_charge': 95, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 2, 'y': 3, 'level': 1, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002154, 'encoder_wheel_1': 3618.841, 'encoder_wheel_2': -5345.805, 'encoder_wheel_3': 5207.461, 'encoder_wheel_4': -3892.431, 'steering_encoder_deg': 91.708, 'pos_sensors': 31, 'gripper_acc_x': 0, 'gripper_acc_y': -1, 'gripper_sensors': 7, 'x_mm': 0, 'y_mm': 1560}, 'expected_duration_s': 3.5999999999999996, 'task_id': 169186, 'status': 'NEW', 'action_history_id': None}=2, {'command_id': 'MOVE', 'param1': 3, 'param2': 0, 'param3': 0, 'box_id': None, 'dist_mm': 1440, 'start_tick': 629, 'finished_tick': 635, 'start_state': {'robot_id': 5, 'timestamp': '2026-03-24T14:22:42.717521Z', 'ready_for_next_command': 2, 'battery_charge': 94, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 67, 'y': 9, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002112, 'encoder_wheel_1': 24580.188000000002, 'encoder_wheel_2': 29053.093, 'encoder_wheel_3': -29055.79, 'encoder_wheel_4': -24580.441, 'steering_encoder_deg': 91.774, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 27780, 'y_mm': 3797}, 'finish_state': {'robot_id': 5, 'timestamp': '2026-03-24T14:22:46.917521Z', 'ready_for_next_command': 2, 'battery_charge': 94, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 1, 'wheels_direction': 1, 'x': 70, 'y': 9, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 0, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32002112, 'encoder_wheel_1': 24580.188000000002, 'encoder_wheel_2': 29053.093, 'encoder_wheel_3': -29055.79, 'encoder_wheel_4': -24580.441, 'steering_encoder_deg': 91.774, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': -1, 'gripper_sensors': 9, 'x_mm': 27780, 'y_mm': 3797}, 'expected_duration_s': 4.2, 'task_id': 164740, 'status': 'NEW', 'callback_success': True, 'action_history_id': None}=2, {'command_id': 'PUT_BOX', 'param1': 30, 'param2': 0, 'param3': 0, 'param4': 100, 'box_id': 32000307, 'dist_mm': 0, 'start_tick': 422, 'finished_tick': 422, 'start_state': {'robot_id': 7, 'timestamp': '2026-06-20T12:12:59.432811Z', 'ready_for_next_command': 3, 'battery_charge': 81, 'lift_state': 2, 'lift_mm': 30, 'gripper_state': 2, 'wheels_direction': 1, 'x': 69, 'y': 6, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': 32000307, 'encoder_wheel_1': 26241.06, 'encoder_wheel_2': 29468.974000000002, 'encoder_wheel_3': -29443.194, 'encoder_wheel_4': -26464.795000000002, 'steering_encoder_deg': 89.682, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 28740, 'y_mm': 3117}, 'finish_state': {'robot_id': 7, 'timestamp': '2026-06-20T12:12:59.432811Z', 'ready_for_next_command': 3, 'battery_charge': 81, 'lift_state': 1, 'lift_mm': 0, 'gripper_state': 2, 'wheels_direction': 1, 'x': 69, 'y': 6, 'level': 0, 'head_state': 2, 'gripper_extension_state': 3, 'wheel_drives': 1, 'head_rotation_deg': 1, 'gripper_extension_mm': 0, 'error_id0': 0, 'error_id1': 0, 'error_id2': 0, 'error_id3': 0, 'error_id4': 0, 'error_id5': 0, 'error_id6': 0, 'error_id7': 0, 'error_id8': 0, 'error_id9': 0, 'speed': 0, 'acceleration': 0, 'box_id': None, 'encoder_wheel_1': 26241.06, 'encoder_wheel_2': 29468.974000000002, 'encoder_wheel_3': -29443.194, 'encoder_wheel_4': -26464.795000000002, 'steering_encoder_deg': 89.682, 'pos_sensors': 31, 'gripper_acc_x': 1, 'gripper_acc_y': 0, 'gripper_sensors': 9, 'x_mm': 28740, 'y_mm': 3117}, 'expected_duration_s': 0.5950704225352113, 'task_id': 185905, 'status': 'NEW', 'action_history_id': None}=2
-- json_data shape: letters+digits=9


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
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 3596, "label": "", "level": 2, "lift_to_stack_bottom_mm": 1890, "lift_tolerance": 45, "max_stack_height_mm": 1247, "mlns_port_type": "M", "short_port_id": 4597, "type": "UNSTORABLE", "x": 68, "y": 2}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 2395, "label": "", "level": 1, "lift_to_stack_bottom_mm": 1925, "lift_tolerance": 45, "max_stack_height_mm": 1260, "mlns_port_type": "M", "short_port_id": 3396, "type": "UNSTORABLE", "x": 37, "y": 5}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 2941, "label": "", "level": 1, "lift_to_stack_bottom_mm": 1925, "lift_tolerance": 45, "max_stack_height_mm": 1260, "mlns_port_type": "M", "short_port_id": 3942, "type": "UNSTORABLE", "x": 51, "y": 5}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 393, "label": "", "level": 0, "lift_to_stack_bottom_mm": 2385, "lift_tolerance": 45, "max_stack_height_mm": 1600, "mlns_port_type": "M", "short_port_id": 1394, "type": "UNSTORABLE", "x": 30, "y": 2}
-- row: {"future_mlns_port_type": null, "gripper_extension_mm": 0, "id": 176, "label": "", "level": 0, "lift_to_stack_bottom_mm": 2385, "lift_tolerance": 45, "max_stack_height_mm": 1600, "mlns_port_type": "M", "short_port_id": 1177, "type": "UNSTORABLE", "x": 13, "y": 6}
-- id: unique values=3744, range=1..3744
-- x: nulls=0, non_nulls=3744, distinct=72
-- x numeric: min=0, median=35.5000, max=71
-- x top_values: 0=52, 1=52, 2=52, 3=52, 4=52, 5=52, 6=52, 7=52, 8=52, 9=52
-- y: nulls=0, non_nulls=3744, distinct=13
-- y numeric: min=0, median=6.0000, max=12
-- y values: 0=288, 1=288, 2=288, 3=288, 4=288, 5=288, 6=288, 7=288, 8=288, 9=288
-- level: nulls=0, non_nulls=3744, distinct=4
-- level numeric: min=0, median=1.5000, max=3
-- level values: 0=936, 1=936, 2=936, 3=936
-- type: nulls=0, non_nulls=3744, distinct=5
-- type values: UNSTORABLE=3637, STORABLE=100, PICKING_PORT=4, BALCONY_PORT=2, CROOKED=1
-- max_stack_height_mm: nulls=0, non_nulls=3744, distinct=5
-- max_stack_height_mm numeric: min=806, median=1260.0000, max=1600
-- max_stack_height_mm values: 806=936, 1260=936, 1600=936, 1247=934, 1300=2
-- lift_to_stack_bottom_mm: nulls=0, non_nulls=3744, distinct=7
-- lift_to_stack_bottom_mm numeric: min=640, median=1890.0000, max=2385
-- lift_to_stack_bottom_mm values: 1555=936, 1890=936, 1925=934, 2385=923, 2365=9, 1500=4, 640=2
-- short_port_id: unique values=3744, range=1..4745
-- label: nulls=0, non_nulls=3744, distinct=1
-- label values: =3744
-- mlns_port_type: nulls=0, non_nulls=3744, distinct=3
-- mlns_port_type values: M=3742, A=1, P=1
-- lift_tolerance: nulls=0, non_nulls=3744, distinct=1
-- lift_tolerance numeric: min=45, median=45.0000, max=45
-- lift_tolerance values: 45=3744
-- gripper_extension_mm: nulls=0, non_nulls=3744, distinct=3
-- gripper_extension_mm numeric: min=0, median=0.0000, max=196
-- gripper_extension_mm values: 0=3738, 196=4, 86=2
-- future_mlns_port_type: all NULL


CREATE TABLE `system_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_time` timestamp NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2093 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=2092
-- LATEST_ROWS: system_session
-- row: {"id": 2092, "start_time": "2026-06-26T11:18:41"}
-- row: {"id": 2091, "start_time": "2026-06-26T08:45:15"}
-- row: {"id": 2090, "start_time": "2026-06-26T08:43:32"}
-- RANDOM_ROWS: system_session
-- row: {"id": 1592, "start_time": "2026-02-17T10:15:15"}
-- row: {"id": 1906, "start_time": "2026-04-29T10:07:58"}
-- row: {"id": 1612, "start_time": "2026-02-23T14:19:49"}
-- row: {"id": 1387, "start_time": "2025-12-17T13:42:19"}
-- row: {"id": 1179, "start_time": "2025-11-18T15:24:03"}
-- id: unique values=2092, range=1..2092
-- start_time: nulls=0, non_nulls=2092, distinct=2092


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
) ENGINE=InnoDB AUTO_INCREMENT=187069 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=40369
-- LATEST_ROWS: task
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-06-25T14:48:11", "delayed_until_ts": null, "finished_ts": "2026-06-25T14:48:13", "id": 187068, "last_replan_ts": "2026-06-25T14:48:13", "n_boxes_ontop": null, "plan_ts": "2026-06-25T14:48:11", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 7, "start_exec_ts": "2026-06-25T14:48:13", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-06-25T14:48:10", "delayed_until_ts": null, "finished_ts": "2026-06-25T14:48:11", "id": 187067, "last_replan_ts": "2026-06-25T14:48:11", "n_boxes_ontop": null, "plan_ts": "2026-06-25T14:48:11", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 7, "start_exec_ts": "2026-06-25T14:48:11", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-06-25T14:48:05", "delayed_until_ts": null, "finished_ts": "2026-06-25T14:48:10", "id": 187066, "last_replan_ts": "2026-06-25T14:48:10", "n_boxes_ontop": null, "plan_ts": "2026-06-25T14:48:07", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 7, "start_exec_ts": "2026-06-25T14:48:07", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- RANDOM_ROWS: task
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": 32000445, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2025-09-13T06:21:30", "delayed_until_ts": null, "finished_ts": "2025-09-13T06:21:51", "id": 14562, "last_replan_ts": null, "n_boxes_ontop": 0, "plan_ts": "2025-09-13T06:21:31", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": null, "start_exec_ts": "2025-09-13T06:21:31", "status": "COMPLETED", "storage_level": 2, "type": "BOX_STORAGE"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-06-11T12:23:10", "delayed_until_ts": null, "finished_ts": "2026-06-11T12:23:11", "id": 183790, "last_replan_ts": "2026-06-11T12:23:11", "n_boxes_ontop": null, "plan_ts": "2026-06-11T12:23:11", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 7, "start_exec_ts": "2026-06-11T12:23:11", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-05-20T10:11:18", "delayed_until_ts": null, "finished_ts": "2026-05-20T10:11:19", "id": 179088, "last_replan_ts": "2026-05-20T10:11:18", "n_boxes_ontop": null, "plan_ts": "2026-05-20T10:11:18", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 5, "start_exec_ts": "2026-05-20T10:11:18", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-04-01T13:26:01", "delayed_until_ts": null, "finished_ts": "2026-04-01T13:26:33", "id": 166769, "last_replan_ts": null, "n_boxes_ontop": null, "plan_ts": "2026-04-01T13:26:02", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 6, "start_exec_ts": "2026-04-01T13:26:02", "status": "COMPLETED", "storage_level": null, "type": "MOVE_ROBOT"}
-- row: {"balcony_stack_id": null, "batch_id": null, "box_id": null, "charging_station_id": null, "child_storage_task_id": null, "create_ts": "2026-06-17T10:58:05", "delayed_until_ts": null, "finished_ts": "2026-06-17T10:58:06", "id": 185881, "last_replan_ts": "2026-06-17T10:58:06", "n_boxes_ontop": null, "plan_ts": "2026-06-17T10:58:06", "port_stack_id": null, "predicted_picking_time_s": null, "robot_id": 7, "start_exec_ts": "2026-06-17T10:58:06", "status": "COMPLETED", "storage_level": null, "type": "RECOVER_ROBOT"}
-- id: unique values=40369, range=273..187068
-- type: nulls=0, non_nulls=40369, distinct=8
-- type values: RECOVER_ROBOT=22206, PREPARE_ROBOTS=8550, MOVE_BOX=5503, BOX_STORAGE=2766, MOVE_ROBOT=863, EXTRACT_BOX=286, EXTRACT_FOR_PICK=116, CHARGE=79
-- status: nulls=0, non_nulls=40369, distinct=3
-- status values: COMPLETED=31276, CANCELLED=9089, FAILED=4
-- create_ts: nulls=0, non_nulls=40369, distinct=35187
-- create_ts top_values: 2026-03-18 12:40:02=22, 2026-03-17 13:22:18=8, 2026-03-18 11:15:02=8, 2026-03-16 14:59:41=7, 2025-12-11 14:11:00=6, 2025-12-12 06:58:03=6, 2025-12-12 07:13:45=6, 2026-03-17 12:47:11=6, 2026-04-22 10:38:19=6, 2026-04-22 10:39:04=6
-- child_storage_task_id: all NULL
-- delayed_until_ts: nulls=38924, non_nulls=1445, distinct=1383
-- delayed_until_ts top_values: 2025-10-24 13:40:14=3, 2026-04-16 10:31:22=3, 2025-07-19 11:49:25=2, 2025-09-24 12:35:49=2, 2025-10-17 08:41:02=2, 2025-10-27 13:28:37=2, 2025-10-27 13:33:08=2, 2025-10-27 13:38:04=2, 2025-10-27 13:48:21=2, 2025-10-28 14:28:35=2
-- finished_ts: nulls=3568, non_nulls=36801, distinct=32051
-- finished_ts top_values: 2026-04-09 13:39:29=6, 2026-03-16 15:37:36=5, 2026-03-16 15:39:08=5, 2026-03-16 15:39:28=5, 2026-04-01 08:26:15=5, 2026-04-22 10:37:09=5, 2026-04-22 10:39:03=5, 2026-04-22 10:39:19=5, 2026-03-16 15:37:00=4, 2026-03-16 15:37:04=4
-- plan_ts: nulls=4528, non_nulls=35841, distinct=32373
-- plan_ts top_values: 2026-04-09 08:32:54=6, 2026-04-01 07:49:53=5, 2026-04-01 08:26:14=4, 2026-04-01 08:26:15=4, 2026-04-01 08:26:16=4, 2026-04-01 12:14:03=4, 2026-04-08 08:42:24=4, 2026-04-08 14:31:53=4, 2026-04-09 11:48:49=4, 2026-04-22 08:47:09=4
-- last_replan_ts: nulls=21546, non_nulls=18823, distinct=16080
-- last_replan_ts top_values: 2026-04-09 08:32:54=6, 2026-04-08 13:51:19=4, 2026-04-08 14:31:51=4, 2026-04-08 14:31:53=4, 2026-04-09 08:32:52=4, 2026-04-22 08:47:09=4, 2026-04-07 11:34:39=3, 2026-04-07 13:59:31=3, 2026-04-08 08:42:24=3, 2026-04-08 10:02:50=3
-- start_exec_ts: nulls=4964, non_nulls=35405, distinct=32222
-- start_exec_ts top_values: 2026-04-01 07:49:53=4, 2026-04-01 08:14:27=4, 2026-04-01 08:26:14=4, 2026-04-01 08:26:15=4, 2026-04-01 08:26:17=4, 2026-04-01 12:14:03=4, 2026-04-08 14:31:53=4, 2026-04-09 08:06:17=4, 2026-04-09 08:32:54=4, 2026-03-16 14:59:41=3
-- box_id: nulls=31698, non_nulls=8671, distinct=686
-- box_id numeric: min=101, median=32000551.0000, max=32005990
-- box_id top_values: 32000183=226, 17000219=118, 32000667=116, 32001146=64, 32000876=54, 32000162=53, 32000490=52, 32000234=51, 32000243=49, 32000854=49
-- balcony_stack_id: all NULL
-- n_boxes_ontop: nulls=37325, non_nulls=3044, distinct=5
-- n_boxes_ontop numeric: min=0, median=0.0000, max=4
-- n_boxes_ontop values: 0=2944, 1=81, 2=14, 3=3, 4=2
-- robot_id: nulls=17215, non_nulls=23154, distinct=7
-- robot_id numeric: min=1, median=6.0000, max=8
-- robot_id values: 6=6184, 7=6176, 5=6133, 1=1748, 8=1444, 3=861, 4=608
-- charging_station_id: nulls=40290, non_nulls=79, distinct=4
-- charging_station_id numeric: min=1, median=1.0000, max=4
-- charging_station_id values: 1=42, 3=18, 2=10, 4=9
-- port_stack_id: nulls=34239, non_nulls=6130, distinct=631
-- port_stack_id numeric: min=41, median=777.0000, max=3660
-- port_stack_id top_values: 927=325, 1253=198, 929=145, 931=104, 907=89, 67=88, 54=85, 171=82, 1252=74, 1331=73
-- predicted_picking_time_s: nulls=38991, non_nulls=1378, distinct=2
-- predicted_picking_time_s numeric: min=0e-10, median=0, max=5.0000000000
-- predicted_picking_time_s values: 0e-10=1254, 5.0000000000=124
-- batch_id: nulls=40253, non_nulls=116, distinct=41
-- batch_id numeric: min=151, median=189.0000, max=208
-- batch_id top_values: 204=22, 184=8, 198=8, 181=6, 183=6, 188=5, 190=4, 162=3, 163=3, 166=3
-- storage_level: nulls=38025, non_nulls=2344, distinct=4
-- storage_level numeric: min=0, median=1.0000, max=3
-- storage_level values: 0=959, 3=643, 1=494, 2=248


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

-- total rows=2
-- ALL_ROWS: timings_put_box
-- row: {"lift_mm": 1, "time_s": 1.0}
-- row: {"lift_mm": 2060, "time_s": 14.5}


CREATE TABLE `timings_take_box` (
  `lift_mm` int(11) NOT NULL,
  `time_s` float DEFAULT NULL,
  PRIMARY KEY (`lift_mm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- total rows=2
-- ALL_ROWS: timings_take_box
-- row: {"lift_mm": 1, "time_s": 1.0}
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
