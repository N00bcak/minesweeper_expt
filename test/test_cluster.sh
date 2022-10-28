for DIM in 20 30 40
do
    for DENSITY in 0.1 0.15 0.2 0.25 0.3
    do
        #for NUM_ITER in 0 5 10 15 20 25 30
        #do
        echo "Received arguments $DIM, $DENSITY" #, $NUM_ITER"
        python3 game_of_life_gen.py -height=$DIM -width=$DIM -mine_density=0.3 -cluster=1 -seed_den=$DENSITY -sample_n=1000 >> log_cluster.txt
        #done
    done
done