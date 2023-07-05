foo :: (Num n) => n -> Num

foo n = 2 + p
        where p = 2 + q
                  where q = n
