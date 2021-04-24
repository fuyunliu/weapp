BEGIN;
--
-- Create model User
--
CREATE TABLE "oauth_user" ("id" serial NOT NULL PRIMARY KEY, "password" varchar(128) NOT NULL, "last_login" timestamp with time zone NULL, "is_superuser" boolean NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" boolean NOT NULL, "is_active" boolean NOT NULL, "date_joined" timestamp with time zone NOT NULL, "phone" varchar(128) NOT NULL, "name_mtime" timestamp with time zone NOT NULL);
CREATE TABLE "oauth_user_groups" ("id" serial NOT NULL PRIMARY KEY, "user_id" integer NOT NULL, "group_id" integer NOT NULL);
CREATE TABLE "oauth_user_user_permissions" ("id" serial NOT NULL PRIMARY KEY, "user_id" integer NOT NULL, "permission_id" integer NOT NULL);
--
-- Create model Profile
--
CREATE TABLE "oauth_profile" ("user_id" integer NOT NULL PRIMARY KEY, "nickname" varchar(64) NOT NULL UNIQUE, "gender" integer NULL, "birthday" date NULL, "location" varchar(64) NOT NULL, "about_me" text NOT NULL, "avatar_hash" varchar(32) NOT NULL, "nick_mtime" timestamp with time zone NOT NULL);
--
-- Create model Region
--
CREATE TABLE "oauth_region" ("id" serial NOT NULL PRIMARY KEY, "name" varchar(32) NOT NULL, "code" varchar(32) NOT NULL, "level" integer NOT NULL, "parent_id" integer NULL);
CREATE INDEX "oauth_user_username_c0895376_like" ON "oauth_user" ("username" varchar_pattern_ops);
ALTER TABLE "oauth_user_groups" ADD CONSTRAINT "oauth_user_groups_user_id_group_id_bc22677c_uniq" UNIQUE ("user_id", "group_id");
ALTER TABLE "oauth_user_groups" ADD CONSTRAINT "oauth_user_groups_user_id_d2d9e19c_fk_oauth_user_id" FOREIGN KEY ("user_id") REFERENCES "oauth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "oauth_user_groups" ADD CONSTRAINT "oauth_user_groups_group_id_65532028_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "oauth_user_groups_user_id_d2d9e19c" ON "oauth_user_groups" ("user_id");
CREATE INDEX "oauth_user_groups_group_id_65532028" ON "oauth_user_groups" ("group_id");
ALTER TABLE "oauth_user_user_permissions" ADD CONSTRAINT "oauth_user_user_permissions_user_id_permission_id_5271e9f9_uniq" UNIQUE ("user_id", "permission_id");
ALTER TABLE "oauth_user_user_permissions" ADD CONSTRAINT "oauth_user_user_permissions_user_id_a47d8ed0_fk_oauth_user_id" FOREIGN KEY ("user_id") REFERENCES "oauth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "oauth_user_user_permissions" ADD CONSTRAINT "oauth_user_user_perm_permission_id_5af9a251_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "oauth_user_user_permissions_user_id_a47d8ed0" ON "oauth_user_user_permissions" ("user_id");
CREATE INDEX "oauth_user_user_permissions_permission_id_5af9a251" ON "oauth_user_user_permissions" ("permission_id");
ALTER TABLE "oauth_profile" ADD CONSTRAINT "oauth_profile_user_id_491913f1_fk_oauth_user_id" FOREIGN KEY ("user_id") REFERENCES "oauth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "oauth_profile_nickname_17beffb7_like" ON "oauth_profile" ("nickname" varchar_pattern_ops);
ALTER TABLE "oauth_region" ADD CONSTRAINT "oauth_region_parent_id_fb8aadf6_fk_oauth_region_id" FOREIGN KEY ("parent_id") REFERENCES "oauth_region" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "oauth_region_parent_id_fb8aadf6" ON "oauth_region" ("parent_id");
COMMIT;
