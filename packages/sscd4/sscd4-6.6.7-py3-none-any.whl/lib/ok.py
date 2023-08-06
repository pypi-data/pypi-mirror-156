def ok():
    print("""
    
#include<stdio.h>
#include<string.h>
int k=0,z=0,i=0,j=0,c=0;
char a[16],ac[20],stk[15],act[10];
void func(){
    stk[z]='E';
    stk[z+1]='\0';
    stk[z+2]='\0';
    printf("\n$%s\t%s$\t%s",stk,a,ac);
    i=i-2;
}
void check()
{
    strcpy(ac,"REDUCE TO E");
    for(z=0; z<c; z++){
        if(stk[z]=='i' && stk[z+1]=='d'){
            stk[z]='E';
            stk[z+1]='\0';
            printf("\n$%s\t%s$\t%s",stk,a,ac);
            j++;
        }
        if(stk[z]=='E' && stk[z+1]=='+' && stk[z+2]=='E')func();
        if(stk[z]=='E' && stk[z+1]=='*' && stk[z+2]=='E')func();        
        if(stk[z]=='(' && stk[z+1]=='E' && stk[z+2]==')')func();   
    }
}
int main()
{
    puts("GRAMMAR is E->E+E \n E->E*E \n E->(E) \n E->id\nEnter input string :");
    gets(a);
    c=strlen(a);
    strcpy(act,"SHIFT->");
    puts("stack \t input \t action");
    for(k=0,i=0; j<c; k++,i++,j++){
        stk[i]=a[j];
        a[j]=' ';
        if(a[j]=='i' && a[j+1]=='d'){
            stk[i+1]=a[j+1];
            stk[i+2]='\0';
            a[j+1]=' ';
            printf("\n$%s\t%s$\t%sid",stk,a,act); 
        }
        else{
            stk[i+1]='\0';
            printf("\n$%s\t%s$\t%ssymbols",stk,a,act); 
        }
        check();
    }
}

    """)