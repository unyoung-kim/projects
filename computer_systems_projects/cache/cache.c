#define _GNU_SOURCE
#include <getopt.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include "cachelab.h"


struct block{
    bool v;
    int tag;
    int time_stamp;
};

bool load_store(struct block *line, long long tag, int e, int time_stamp, int *hit, int *miss, int *evict);
void modify(struct block *line, long long tag, int e, int time_stamp, int *hit, int *miss, int *evict);
int least_recently_used(struct block *line, int e);


int main(int argc, char *argv[])
{
    int index = 0;
    int s = 0;
    int e = 0;
    int b = 0;
    char* file_name;

    //Read Command line 
    while ((index = getopt(argc, argv,"s:E:b:t:")) != -1)
    {
        switch(index){
            case 's':
            s = atoi(optarg);
            break;

            case 'E':
            e = atoi(optarg);
            break;

            case 'b':
            b = atoi(optarg);
            break;

            case 't':
            file_name = optarg;
            break;

            default:
                break;
        }
    }

    //Dynamically allocate Cache in a 2D array
    struct block **cache; 
    cache = malloc(sizeof(struct block*) * pow(2,s));

    if(cache == NULL){
		fprintf(stderr, "out of memory\n");
		}

    for(int i = 0; i < pow(2,s); i++){
        cache[i] = malloc(sizeof(struct block) * e);
        if(cache[i] == NULL){
			fprintf(stderr, "out of memory\n");
			}
        //Initialize valid bits
        for(int j = 0; j < e; j++){
            cache[i][j].v = 0;
        }
    }

    int hit = 0;
    int miss = 0;
    int evict = 0;
    
   int global_time_stamp = 1; 

    char *line = NULL;
    size_t length;
    ssize_t read;
    FILE *trace_file;

    //Read File
    trace_file = fopen(file_name, "r");

    while((read = getline(&line, &length, trace_file)) != -1)
    {

        // each iteration, one line of the input file will be stored
        // in the variable "line"
        if(line[0] == ' ')
        {
            //Parse address and Operation Type
            char* operation = strtok(line, " ");
            long long address = strtoull(strtok(strtok(NULL, line), ","), NULL, 16);

            long long set = (address >> b) & (long long)(pow(2,s) - 1);      //Extract setbits
            long long tag = (address >> (b+s)) & (long long)(0x7fffffffffffffff>>(b+s-1));     //Extract tag bits

            if (operation[0] == 'L' || operation[0] == 'S'){
                load_store(cache[set], tag, e, global_time_stamp, &hit, &miss, &evict);
            } else if (operation[0] == 'M'){
                modify(cache[set], tag, e, global_time_stamp, &hit, &miss, &evict);
            } 

            global_time_stamp ++; //Update operation number for LRU
        } 
    }

    for(int i=0; i<s; i++){
        free(cache[i]);
    }
    free(cache);

    printSummary(hit, miss, evict);
    
    return 0;
}

/*
Check if the line is a hit. Update the cache by either restoring it or replacing it depending on the situation,
Update hits, missses, and evictions

<Parameters>
line: Command line
tag: tag bit
e: Number of lines per set
hit: number of hits
miss: number of misses
evict: number of evicts

<Return>
True if it is a hit, false if it is not
*/
bool load_store(struct block *line, long long tag, int e, int time_stamp, int *hit, int *miss, int *evict){
    bool empty = false;
    int empty_block;

    for(int i=0; i < e; i++){
        //Search if there's a match in tag
        if(line[i].v == 1 && line[i].tag == tag){
            line[i].time_stamp = time_stamp;
            (*hit)++;
            return true;
        }else if(line[i].v == 0){
            empty = true;
            empty_block = i;
        }
    }
    //Miss, Restore
    if(empty){
        line[empty_block].v = 1;
        line[empty_block].tag = tag;
        line[empty_block].time_stamp = time_stamp;
        (*miss)++;
        return false;
    } 

    //Miss, Eviction, Replace
    int lru = least_recently_used(line, e);
    line[lru].tag = tag;
    line[lru].time_stamp = time_stamp;
    (*miss)++;
    (*evict)++;
    return false;
}

/*
Modify the cache and update the number of hits, misses, and evicts

<Parameters>
line: Command line
tag: tag bit
e: Number of lines per set
hit: number of hits
miss: number of misses
evict: number of evicts
*/
void modify(struct block *line, long long tag, int e, int time_stamp, int *hit, int *miss, int *evict){

    bool empty = false;
    int empty_block;
    bool load = false;

    //Load first
    for(int i = 0; i < e; i++){
        if(line[i].v == 1 && line[i].tag == tag){
            line[i].time_stamp = time_stamp;
            (*hit)++;
            load = true;
            break;

        } else if(line[i].v == 0){
            empty = true;
            empty_block = i;
        }
    }

    //If there is no match in tag and the line has an empty block, Load is a simple miss
    if(!load && empty){
        line[empty_block].v = 1;
        line[empty_block].tag = tag;
        line[empty_block].time_stamp = time_stamp;
        (*miss)++;

    } else if(!load && !empty){    //Miss and eviction
        int lru = least_recently_used(line, e);
        line[lru].v = 1;
        line[lru].tag = tag;
        line[lru].time_stamp = time_stamp;
        (*miss)++; 
        (*evict)++;
    }
    //Then Store is an automatic hit
    (*hit)++;

    return;
}

/*
Find the least recently used block within a set

<Parameters>
line: 
e:

<Return>
Index of the least recently used block
*/
int least_recently_used(struct block *line, int e){
    int smallest = line[0].time_stamp;
    int index = 0;

    for(int i = 1; i < e; i++){
        if (line[i].time_stamp != 0 && line[i].time_stamp < smallest){
            smallest = line[i].time_stamp;
            index = i; 
        }
    }

    return index;
}


