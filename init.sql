DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;

-- Create doctors table
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) NOT NULL
);

-- Create appointments table
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    patient_name VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    UNIQUE (doctor_id, start_time)
);

-- Insert sample doctors
INSERT INTO doctors (name, specialty) VALUES
('Терапевт Иванов И.И.', 'Терапевт'),
('Терапевт Петров П.П.', 'Терапевт'),
('Терапевт Сидоров С.С.', 'Терапевт');

-- Insert sample appointments (mos doctor_id lar bo‘yicha)
INSERT INTO appointments (doctor_id, patient_name, patient_phone, start_time, end_time) VALUES
(1, 'Анна Иванова', '+7-900-123-45-67', '2025-07-04 10:00:00', '2025-07-04 10:30:00'),
(2, 'Мария Сидорова', '+7-900-765-43-21', '2025-07-04 11:30:00', '2025-07-04 12:00:00'),
(3, 'Дмитрий Смирнов', '+7-900-333-22-11', '2025-07-05 09:00:00', '2025-07-05 09:30:00');
