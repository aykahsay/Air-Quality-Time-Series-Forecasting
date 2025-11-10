/*
==================================
Safe Database and Schemas Setup
==================================

Script Purpose:
This script safely creates a database named 'AirQualityDB' and three schemas: 'bronze', 'silver', 'gold'.
It checks if the database or schemas exist before creating them, so no existing data is lost.

Note:
Running this script multiple times is safe; it will not drop or overwrite any existing objects.
*/

USE master;
GO

-- Create database if it does not exist
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'AirQualityDB')
BEGIN
    CREATE DATABASE AirQualityDB;
    PRINT 'Database AirQualityDB created successfully.';
END
ELSE
BEGIN
    PRINT 'Database AirQualityDB already exists. Skipping creation.';
END;
GO

USE AirQualityDB;
GO

-- Create bronze schema if it does not exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'bronze')
BEGIN
    EXEC('CREATE SCHEMA bronze');
    PRINT 'Schema bronze created successfully.';
END
ELSE
BEGIN
    PRINT 'Schema bronze already exists. Skipping creation.';
END;
GO

-- Create silver schema if it does not exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'silver')
BEGIN
    EXEC('CREATE SCHEMA silver');
    PRINT 'Schema silver created successfully.';
END
ELSE
BEGIN
    PRINT 'Schema silver already exists. Skipping creation.';
END;
GO

-- Create gold schema if it does not exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'gold')
BEGIN
    EXEC('CREATE SCHEMA gold');
    PRINT 'Schema gold created successfully.';
END
ELSE
BEGIN
    PRINT 'Schema gold already exists. Skipping creation.';
END;
GO
