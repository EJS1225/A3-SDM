DROP TYPE IF EXISTS situacao1, situacao2;
-- Endereços dos tutores e clinica
CREATE TABLE IF NOT EXISTS Enderecos(
    ID_ENDERECO INT GENERATED ALWAYS AS IDENTITY,
	CEP VARCHAR(8) NOT NULL,
	logradouro VARCHAR(150) NOT NULL,
	DDD INT NOT NULL,
	numero_telefone VARCHAR(11),
	bairro VARCHAR(100) NOT NULL,
	cidade VARCHAR(100) NOT NULL,
	UF VARCHAR(2) NOT NULL,
	CodIBGE VARCHAR(8) NOT NULL,
	PRIMARY KEY(id_endereco),
	CONSTRAINT DDD_Valido CHECK (DDD <= 99)
);

CREATE TABLE IF NOT EXISTS tutores(
    ID_tutores INT GENERATED ALWAYS AS IDENTITY,
	Nome VARCHAR(255) NOT NULL,
	Sobrenome VARCHAR(255) NOT NULL,
	Telefone VARCHAR(50),
	Email VARCHAR(255) NOT NULL,
	DataCadastro DATE NOT NULL,
	CadastroConfirmado BOOL NOT NULL,
	CPF_tutor VARCHAR(11) NOT NULL,
	EnderecoAssociado INT NOT NULL,
	UNIQUE (email, cpf_tutor),
	PRIMARY KEY(ID_tutores),
	CONSTRAINT fk_local
	FOREIGN KEY (enderecoassociado)
	REFERENCES enderecos(id_endereco)
);

-- Especies
CREATE TABLE IF NOT EXISTS especies(
    ID_ESPECIES INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	Nome VARCHAR(150) NOT NULL UNIQUE,
	descricao TEXT,
	situacao TEXT
);

-- Raças
CREATE TABLE IF NOT EXISTS racas (
    ID_RACAS INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	Nome VARCHAR(250) NOT NULL,
	descricao TEXT,
	especie_associada INT,
	situacao TEXT,
	CONSTRAINT fk_especie
	FOREIGN KEY (especie_associada)
	REFERENCES especies(id_especies)
);

CREATE TABLE IF NOT EXISTS Veterinarios(
    ID_VETS INT GENERATED ALWAYS AS IDENTITY,
	Nome VARCHAR(255) NOT NULL,
	Sobrenome VARCHAR(255) NOT NULL,
	Telefone VARCHAR(50),
	Email VARCHAR(255) NOT NULL,
	DataCadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CPF_vet VARCHAR(11),
	Datahora_UltAcesso TIMESTAMP NOT NULL,
	Cadastrado BOOL DEFAULT FALSE,
	senhaconfirmada BOOL DEFAULT FALSE,
	ativo BOOL DEFAULT FALSE,
	hash_senha TEXT NOT NULL,
	CRMV_Num VARCHAR(50),
	UF_CRMV VARCHAR(2),
	PRIMARY KEY (ID_VETS),
	UNIQUE (email, hash_senha, cpf_vet)
);

-- Registro de Animais e Microchip RFID
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
	PRIMARY KEY (id_animais),
	CONSTRAINT fk_tutor 
	FOREIGN KEY (tutor_id) 
	REFERENCES tutores(id_tutores),
	CONSTRAINT fk_especie
	FOREIGN KEY (especie)
	REFERENCES especies(id_especies),
	CONSTRAINT fk_raca
	FOREIGN KEY (raca)
	REFERENCES racas(id_racas),
	CONSTRAINT fk_vet
	FOREIGN KEY (Vet_RFID_vinculo)
	REFERENCES veterinarios(id_vets)
);

CREATE TYPE situacao1 AS ENUM ('agendada', 'realizada', 'cancelada', 'não compareceu');
-- Registro de consultas
CREATE TABLE IF NOT EXISTS registro_consultas(
    ID_CONSULTA INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	Animal_atendido INT NOT NULL,
	Vet_responsavel INT NOT NULL,
	datahora_atendimento TIMESTAMP NOT NULL,
	motivo TEXT,
	Anamnese TEXT,
	Sintomas VARCHAR(1000),
	diagnostico TEXT,
	Tratamento TEXT,
	Prescr_Medicam VARCHAR(750),
	peso_kg VARCHAR(5) NOT NULL,
	temperatura VARCHAR(50),
	Obser TEXT,
	situacao_atual situacao1 NOT NULL,
	CONSTRAINT fk_vet
	FOREIGN KEY (vet_responsavel)
	REFERENCES veterinarios(id_vets),
	CONSTRAINT fk_anim
	FOREIGN KEY (animal_atendido)
	REFERENCES animais(id_animais)
);

CREATE TYPE situacao2 AS ENUM ('agendada', 'aplicada', 'cancelada');
-- Registro  de vacinas
CREATE TABLE IF NOT EXISTS registro_vacinas(
    ID_VACINA INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	Animal_atendido INT NOT NULL,
	Vet_responsavel INT NOT NULL,
	nome_vacina VARCHAR(255) NOT NULL,
	tipo_vacina VARCHAR(200) NOT NULL,
	anitrrabica_ind TEXT,
	fabricante VARCHAR(255) NOT NULL,
	lote TEXT,
	data_vacina DATE,
	dose_vacina VARCHAR(100),
	via_aplicacao VARCHAR(100),
	data_prox_dose DATE,
	validade_lote DATE,
	observ TEXT,
	situacoo situacao2 NOT NULL,
	CONSTRAINT fk_vet
	FOREIGN KEY (vet_responsavel)
	REFERENCES veterinarios(id_vets),
	CONSTRAINT fk_anim
	FOREIGN KEY (animal_atendido)
	REFERENCES animais(id_animais)
);

-- SELECT verificar_cpf()