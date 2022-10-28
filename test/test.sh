for DIM in 20 30 40
do
    for DENSITY in 0.3
    do
        for NUM_ITER in 0 5 10 15 20 25 30
        do
            echo "Received arguments $DIM, $DENSITY, $NUM_ITER"
            python3 game_of_life_gen.py -height=$DIM -width=$DIM -mine_density=$DENSITY -gol=1 -gol_iter=$NUM_ITER -sample_n=1000 >> log.txt
        done
    done
done