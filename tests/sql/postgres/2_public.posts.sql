DROP TABLE IF EXISTS public.posts CASCADE;
CREATE TABLE public.posts
(
    post_id      SERIAL PRIMARY KEY,
    user_id      INT REFERENCES public.users (user_id),
    post_title   VARCHAR(255) NOT NULL,
    post_content TEXT,
    hello        VARCHAR(255) NOT NULL DEFAULT 'Hello World',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER SEQUENCE public.posts_post_id_seq OWNED BY NONE;
INSERT INTO public.posts (user_id, post_title, post_content, created_at)
VALUES (1, 'Hello World', 'This is my first post', '2019-01-01 00:00:00'),
       (2, 'Hey Universe', 'This is my initial tweet', '2019-01-01 00:00:00'),
       (3, 'Hi Galaxy', 'This is my first message', '2019-01-01 00:00:00');
ALTER SEQUENCE public.posts_post_id_seq OWNED BY public.posts.post_id;
