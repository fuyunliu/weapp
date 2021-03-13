BEGIN;
--
-- Create model Tag
--
CREATE TABLE "blog_tag" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(30) NOT NULL, "slug" varchar(50) NOT NULL UNIQUE);
--
-- Create model Category
--
CREATE TABLE "blog_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(30) NOT NULL, "slug" varchar(50) NOT NULL UNIQUE, "parent_id" integer NOT NULL REFERENCES "blog_category" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Article
--
CREATE TABLE "blog_article" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(64) NOT NULL, "body" text NOT NULL, "body_html" text NOT NULL, "abstract" text NOT NULL, "draft" bool NOT NULL, "created" datetime NOT NULL, "updated" datetime NOT NULL, "slug" varchar(50) NOT NULL UNIQUE, "author_id" integer NOT NULL REFERENCES "accounts_fireuser" ("id") DEFERRABLE INITIALLY DEFERRED, "category_id" integer NOT NULL REFERENCES "blog_category" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "blog_article_tags" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "article_id" integer NOT NULL REFERENCES "blog_article" ("id") DEFERRABLE INITIALLY DEFERRED, "tag_id" integer NOT NULL REFERENCES "blog_tag" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "blog_tag_name_c5718cc8" ON "blog_tag" ("name");
CREATE INDEX "blog_category_name_92eb1483" ON "blog_category" ("name");
CREATE INDEX "blog_category_parent_id_2d80fe5c" ON "blog_category" ("parent_id");
CREATE INDEX "blog_article_title_3c514952" ON "blog_article" ("title");
CREATE INDEX "blog_article_author_id_905add38" ON "blog_article" ("author_id");
CREATE INDEX "blog_article_category_id_7e38f15e" ON "blog_article" ("category_id");
CREATE UNIQUE INDEX "blog_article_tags_article_id_tag_id_b78a22e9_uniq" ON "blog_article_tags" ("article_id", "tag_id");
CREATE INDEX "blog_article_tags_article_id_82c02dd6" ON "blog_article_tags" ("article_id");
CREATE INDEX "blog_article_tags_tag_id_88eb3ed9" ON "blog_article_tags" ("tag_id");
COMMIT;
