using namespace std;
#include<iostream>
#include <stdlib.h>
#include <ctime>


void print_array(int **a, int row, int col) {
	for (size_t i = 0; i < row; ++i){
		for (size_t j = 0; j < col; ++j)
			cout << a[i][j] << " ";
		cout << endl;
	}
}

void shift_neg(int **a, int row, int col, int dx, int dy) {
	dx = -dx;
	dy = -dy;  
	for (int i = row-1; i >= 0; --i){
		for (int j = col-1; j >= 0; --j){
			if(i+dy<row && j+dx<col)
				a[i+dy][j+dx] = a[i][j];
				a[i][j] = 0;
		}
	}
}

void shift_pos(int **a, int row, int col, int dx, int dy) {
	for (int i = 0; i < row; ++i){
		for (int j = 0; j < col; ++j){
			if(i+dy<row  && j+dx<col )
				a[i][j] = a[i+dy][j+dx];
			else
				a[i][j] = 0;
		}
	}
}


void shift_array(int **a, int row, int col, int dx, int dy) {
	if(dx<0 && dy<0){
		shift_neg(a, row, col, dx, dy);
		return;
	} else if(dx>0 && dy>0){
		shift_pos(a, row, col, dx, dy);
		return;
	} else {
		if(dx<0){
			shift_neg(a, row, col, dx, 0);
			shift_pos(a, row, col, 0, dy);
			return;
		}
		if(dy<0){
			shift_neg(a, row, col, 0, dy);
			shift_pos(a, row, col, dx, 0);
			return;
		}
	}
}
      

int main() {
	clock_t    start;
	const int n = 2000; 
	int **array;
	array = new int *[n];
	for (int i = 0; i < n; ++i){
		array[i] = new int[n]; 
		for (int j = 0; j < n; ++j)
			array[i][j] = rand() % 10;
	}
	// print_array(array,  n,  n);
	// cout << "-------------" << endl;
	start = clock();
	shift_array(array,n,n,20,-20);
	cout << "Time: " << (clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << endl;
	// print_array( array,  n,  n);
	// cout << "-------------" << endl;
	return 0;
}