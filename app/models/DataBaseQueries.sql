-- ============================================================
-- Student Management System — MSSQL Setup Script
-- Execution order: Database → Users → Students → AuditLogs → Indexes → Permissions
-- ============================================================


-- ============================================================
-- 1. Create Database
-- ============================================================
USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'student_mgmt')
    CREATE DATABASE student_mgmt COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

USE student_mgmt;
GO


-- ============================================================
-- 2. dbo.Users  (root entity — no FK dependencies)
-- ============================================================
IF OBJECT_ID('dbo.Users', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Users (
        user_id          INT            IDENTITY(1,1)        NOT NULL,
        username         NVARCHAR(50)                        NOT NULL,
        email            NVARCHAR(255)                       NOT NULL,
        hashed_password  NVARCHAR(255)                       NOT NULL,  -- bcrypt hash
        role             NVARCHAR(20)                        NOT NULL
                             CONSTRAINT CK_Users_role CHECK (role IN ('admin', 'student')),
        is_active        BIT            DEFAULT 1            NOT NULL,  -- 0 = soft-deleted
        created_at       DATETIME2(0)   DEFAULT GETUTCDATE() NOT NULL,
        updated_at       DATETIME2(0)                        NULL,

        CONSTRAINT PK_Users          PRIMARY KEY (user_id),
        CONSTRAINT UQ_Users_email    UNIQUE (email),
        CONSTRAINT UQ_Users_username UNIQUE (username)
    );
    PRINT 'Table dbo.Users created.';
END
ELSE
    PRINT 'Table dbo.Users already exists — skipping.';
GO


-- ============================================================
-- 3. dbo.Students  (FK → Users)
-- ============================================================
IF OBJECT_ID('dbo.Students', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Students (
        student_id      INT            IDENTITY(1,1)        NOT NULL,
        user_id         INT                                  NOT NULL,  -- one-to-one FK
        first_name      NVARCHAR(100)                       NOT NULL,
        last_name       NVARCHAR(100)                       NOT NULL,
        email           NVARCHAR(255)                       NOT NULL,  -- may differ from login email
        phone           NVARCHAR(20)                        NULL,
        date_of_birth   DATE                                NULL,
        gender          NVARCHAR(10)                        NULL,
        department      NVARCHAR(100)                       NOT NULL,
        major           NVARCHAR(100)                       NOT NULL,
        enrollment_year SMALLINT                            NOT NULL,
        year_of_study   TINYINT                             NOT NULL
                            CONSTRAINT CK_Students_year CHECK (year_of_study BETWEEN 1 AND 6),
        gpa             DECIMAL(3, 2)                       NULL       -- DECIMAL avoids float rounding
                            CONSTRAINT CK_Students_gpa  CHECK (gpa BETWEEN 0.00 AND 4.00),
        status          NVARCHAR(20)   DEFAULT 'active'     NOT NULL
                            CONSTRAINT CK_Students_status CHECK (status IN ('active', 'inactive', 'graduated')),
        address         NVARCHAR(500)                       NULL,
        created_at      DATETIME2(0)   DEFAULT GETUTCDATE() NOT NULL,
        updated_at      DATETIME2(0)                        NULL,

        CONSTRAINT PK_Students         PRIMARY KEY (student_id),
        CONSTRAINT FK_Students_Users   FOREIGN KEY (user_id) REFERENCES dbo.Users (user_id)
                                           ON DELETE CASCADE ON UPDATE NO ACTION,
        CONSTRAINT UQ_Students_user_id UNIQUE (user_id),
        CONSTRAINT UQ_Students_email   UNIQUE (email)
    );
    PRINT 'Table dbo.Students created.';
END
ELSE
    PRINT 'Table dbo.Students already exists — skipping.';
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.Students') AND name = 'IX_Students_department')
    CREATE INDEX IX_Students_department ON dbo.Students (department);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.Students') AND name = 'IX_Students_gpa')
    CREATE INDEX IX_Students_gpa ON dbo.Students (gpa);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.Students') AND name = 'IX_Students_status')
    CREATE INDEX IX_Students_status ON dbo.Students (status);
GO


-- ============================================================
-- 4. dbo.AuditLogs  (FK → Users + Students | append-only)
-- ============================================================
IF OBJECT_ID('dbo.AuditLogs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.AuditLogs (
        log_id        BIGINT         IDENTITY(1,1)        NOT NULL,  -- BIGINT for high volume
        student_id    INT                                 NULL,       -- SET NULL on student delete
        changed_by    INT                                 NOT NULL,
        action        NVARCHAR(10)                        NOT NULL
                          CONSTRAINT CK_AuditLogs_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE')),
        endpoint      NVARCHAR(255)                       NOT NULL,
        field_changed NVARCHAR(100)                       NULL,       -- UPDATE only
        old_value     NVARCHAR(MAX)                       NULL,       -- JSON snapshot
        new_value     NVARCHAR(MAX)                       NULL,       -- JSON snapshot
        ip_address    NVARCHAR(45)                        NULL,       -- supports IPv6
        timestamp     DATETIME2(0)   DEFAULT GETUTCDATE() NOT NULL,

        CONSTRAINT PK_AuditLogs PRIMARY KEY (log_id),

        -- Audit row survives student deletion
        CONSTRAINT FK_AuditLogs_Students FOREIGN KEY (student_id)
            REFERENCES dbo.Students (student_id) ON DELETE SET NULL  ON UPDATE NO ACTION,

        -- Cannot delete a User who has audit records
        CONSTRAINT FK_AuditLogs_Users    FOREIGN KEY (changed_by)
            REFERENCES dbo.Users (user_id)    ON DELETE NO ACTION ON UPDATE NO ACTION
    );
    PRINT 'Table dbo.AuditLogs created.';
END
ELSE
    PRINT 'Table dbo.AuditLogs already exists — skipping.';
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.AuditLogs') AND name = 'IX_AuditLogs_student')
    CREATE INDEX IX_AuditLogs_student   ON dbo.AuditLogs (student_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.AuditLogs') AND name = 'IX_AuditLogs_timestamp')
    CREATE INDEX IX_AuditLogs_timestamp ON dbo.AuditLogs (timestamp DESC);
GO


-- ============================================================
-- 5. App user + permissions (least-privilege)
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'app_user')
    CREATE LOGIN app_user WITH PASSWORD = 'AppStr0ngP@ss!';
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'app_user')
    CREATE USER app_user FOR LOGIN app_user;
GO

GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Users    TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Students TO app_user;

-- AuditLogs is append-only for app_user
GRANT  SELECT, INSERT ON dbo.AuditLogs TO app_user;
DENY   UPDATE         ON dbo.AuditLogs TO app_user;
DENY   DELETE         ON dbo.AuditLogs TO app_user;
GO


-- ============================================================
-- 6. Verify schema
-- ============================================================

-- Tables
SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo' ORDER BY TABLE_NAME;

-- Columns
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo' ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Foreign keys
SELECT
    fk.name                           AS constraint_name,
    tp.name                           AS parent_table,
    cp.name                           AS parent_column,
    tr.name                           AS referenced_table,
    fk.delete_referential_action_desc AS on_delete
FROM sys.foreign_keys AS fk
JOIN sys.foreign_key_columns AS fkc ON fk.object_id       = fkc.constraint_object_id
JOIN sys.tables  AS tp ON fkc.parent_object_id            = tp.object_id
JOIN sys.columns AS cp ON fkc.parent_object_id            = cp.object_id AND fkc.parent_column_id    = cp.column_id
JOIN sys.tables  AS tr ON fkc.referenced_object_id        = tr.object_id
ORDER BY tp.name;

-- Indexes
SELECT t.name AS table_name, i.name AS index_name, i.is_unique, i.is_primary_key
FROM sys.indexes AS i
JOIN sys.tables  AS t ON i.object_id = t.object_id
WHERE t.schema_id = SCHEMA_ID('dbo') AND i.name IS NOT NULL
ORDER BY t.name, i.name;

PRINT ' Schema verification complete.';
GO