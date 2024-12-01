import System.Environment
import Data.List

-- Convert input file to a list of columns
input_parsed :: String -> [[Integer]]
input_parsed = transpose . map (map read . words) . lines

-- Since Data.List size outputs Int, not Integer
count :: [a] -> Integer
count = sum . map (\_ -> 1)

-- Caluculate part 1
part1 :: String -> Integer
part1 input = sum $ map abs $ zipWith (-) ls rs
    where [ls, rs] = map sort $ input_parsed input

-- Caluculate part 2
part2 :: String -> Integer
part2 input = sum [ ((*l) . count . filter (==l)) rs | l <- ls ]
    where [ls, rs] = map sort $ input_parsed input

main :: IO ()
main = do
    [input_file] <- getArgs

    putStrLn ("Reading file " ++ input_file)

    fileContent <- readFile input_file

    putStr "Result part 1: "
    print $ part1 $ fileContent
    putStr "Result part 2: "
    print $ part2 $ fileContent

    return ()
