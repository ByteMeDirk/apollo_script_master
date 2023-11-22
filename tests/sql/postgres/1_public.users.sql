-- Table with constraints
DROP TABLE IF EXISTS public.users CASCADE;
CREATE TABLE public.users
(
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(50) UNIQUE  NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER SEQUENCE public.users_user_id_seq OWNED BY NONE;
INSERT INTO public.users (user_id, username, email)
VALUES (1, 'user1', 'user1@email.com'),
       (2, 'user2', 'user2email.com'),
       (3, 'user3', 'user3email.com');
ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;
