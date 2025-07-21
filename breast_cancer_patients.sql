USE breast_cancer_patients;
SHOW TABLES;
CREATE TABLE `breast_cancer_patients` (
  `patient_id` INT NOT NULL AUTO_INCREMENT,
  `patient_name` VARCHAR(100) DEFAULT NULL,
  `surname` VARCHAR(100) DEFAULT NULL,
  `age` INT DEFAULT NULL,
  `gender` VARCHAR(20) DEFAULT NULL,
  `address` VARCHAR(255) DEFAULT NULL,
  `mobile_number` VARCHAR(20) DEFAULT NULL,
  `date_of_consultation` DATE DEFAULT NULL,
  `referring_physician` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
