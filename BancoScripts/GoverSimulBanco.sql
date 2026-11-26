CREATE TABLE IF NOT EXISTS animais(
    ID_ANIMAIS INT GENERATED ALWAYS AS IDENTITY,
	tutor_id INT NOT NULL,
	Nome VARCHAR(250) NOT NULL,
	idade_estimada INT NOT NULL,
	sexo VARCHAR(1) NOT NULL,
	cor VARCHAR(100) NOT NULL,
	peso_atual_kg VARCHAR(5) NOT NULL,
	especie INT NOT NULL,
	raca INT NOT NULL,
    situacao TEXT,
	ID_RFID INT UNIQUE,
	data_RFID_vinculo DATE NOT NULL,
	Vet_RFID_vinculo INT NOT NULL,
	PRIMARY KEY(id_animais)
);

CREATE TYPE situacao2 AS ENUM ('agendada', 'aplicada', 'cancelada');

CREATE TABLE IF NOT EXISTS registro_vacinas(
    ID_VACINA INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	Animal_atendido INT NOT NULL,
	Vet_responsavel INT NOT NULL,
	nome_vacina VARCHAR(255) NOT NULL,
	tipo_vacina VARCHAR(200) NOT NULL,
	antirrabica_ind BOOLEAN,
	fabricante VARCHAR(255) NOT NULL,
	lote TEXT,
	data_vacina DATE,
	dose_vacina VARCHAR(100),
	via_aplicacao VARCHAR(100),
	data_prox_dose DATE,
	validade_lote DATE,
	observ TEXT,
	situacao situacao2 NOT NULL
);

