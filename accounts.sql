BEGIN;
--
-- Create model FireUser
--
CREATE TABLE "accounts_fireuser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "nickname" varchar(64) NOT NULL, "location" varchar(64) NOT NULL, "about_me" text NOT NULL, "avatar_hash" varchar(32) NOT NULL);
CREATE TABLE "accounts_fireuser_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fireuser_id" integer NOT NULL REFERENCES "accounts_fireuser" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "accounts_fireuser_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fireuser_id" integer NOT NULL REFERENCES "accounts_fireuser" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "accounts_fireuser_groups_fireuser_id_group_id_28e83df9_uniq" ON "accounts_fireuser_groups" ("fireuser_id", "group_id");
CREATE INDEX "accounts_fireuser_groups_fireuser_id_5639bb52" ON "accounts_fireuser_groups" ("fireuser_id");
CREATE INDEX "accounts_fireuser_groups_group_id_1edafcc6" ON "accounts_fireuser_groups" ("group_id");
CREATE UNIQUE INDEX "accounts_fireuser_user_permissions_fireuser_id_permission_id_4388fa30_uniq" ON "accounts_fireuser_user_permissions" ("fireuser_id", "permission_id");
CREATE INDEX "accounts_fireuser_user_permissions_fireuser_id_010b68af" ON "accounts_fireuser_user_permissions" ("fireuser_id");
CREATE INDEX "accounts_fireuser_user_permissions_permission_id_be50a715" ON "accounts_fireuser_user_permissions" ("permission_id");
COMMIT;
