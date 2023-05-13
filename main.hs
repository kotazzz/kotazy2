infixr 5 :?
data List a = Nil | a :? (List a) 
              deriving (Show,Read,Eq,Ord)

main = do
    print (0 :? 1 :? Nil)