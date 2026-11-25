-- Step 2 of 2: create the two tables. Run this after 01_create_database.sql.
-- The DROP lines let you re-run the file from scratch. Appointments are dropped first
-- because they point to clinics with a foreign key.
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS clinics;

-- One row per clinic. temp_c is NULL when the weather API could not be reached.
CREATE TABLE clinics (
  clinic_id    VARCHAR(5) PRIMARY KEY,
  clinic_name  VARCHAR(40) NOT NULL,
  city         VARCHAR(20) NOT NULL,
  tier         VARCHAR(10),
  latitude     DECIMAL(8,4),
  longitude    DECIMAL(8,4),
  temp_c       DECIMAL(5,1)
);

-- One row per booking. clinic_id must exist in clinics (foreign key).
CREATE TABLE appointments (
  appointment_id   VARCHAR(8) PRIMARY KEY,
  patient_id       VARCHAR(8) NOT NULL,
  clinic_id        VARCHAR(5) NOT NULL,
  booked_on        DATE,
  appt_date        DATE,
  age              INT,
  gender           VARCHAR(1),
  distance_km      DECIMAL(5,1),
  fee_inr          INT,
  booking_channel  VARCHAR(10),
  visit_type       VARCHAR(12),
  reminder_sent    VARCHAR(3),
  prior_no_shows   INT,
  status           VARCHAR(10),
  lead_days        INT,
  no_show          INT,
  FOREIGN KEY (clinic_id) REFERENCES clinics (clinic_id)
);
