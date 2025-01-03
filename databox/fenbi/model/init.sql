CREATE TABLE fenbi_paper
(
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    paper_id    BIGINT NOT NULL,
    name        VARCHAR(100),
    create_time DATETIME,
    update_time DATETIME,
    is_deleted  BOOLEAN,
    KEY         idx_paper_id (paper_id)
);

CREATE TABLE fenbi_material
(
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    material_id BIGINT NOT NULL,
    content     TEXT,
    create_time DATETIME,
    update_time DATETIME,
    is_deleted  BOOLEAN,
    KEY         idx_material_id (material_id)
);

CREATE TABLE fenbi_question
(
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    question_id  BIGINT NOT NULL,
    content      TEXT,
    chapter_name VARCHAR(100),
    module       VARCHAR(50),
    option_type  INT,
    options      TEXT,
    answer       TEXT,
    material_ids TEXT,
    paper_id     BIGINT,
    create_time  DATETIME,
    update_time  DATETIME,
    is_deleted   BOOLEAN,
    KEY          idx_question_id (question_id),
    KEY          idx_paper_id (paper_id)
);