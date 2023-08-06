def ok():
    print("""
    
#include<stdio.h>
#include<stdlib.h>
void FIFO(char [ ],char [ ],int,int);
void lru(char [ ],char [ ],int,int);
void main(){
    int ch,YN=1,i,l,f;
    char F[10],s[25];
    printf("\n Enter the no of empty frames: ");
    scanf("%d",&f);
    printf("\n Enter the length of the string: ");
    scanf("%d",&l);
    printf("\n Enter the string: ");
    scanf("%s",s);
    for(i=0;i<f;i++)F[i]=-1;
    printf("\n*********** FIFO ***********\n");
    FIFO(s,F,l,f);
    for(i=0;i<f;i++)F[i]=-1;
    printf("\n\n*********** LRU ***********\n");
    lru(s,F,l,f);
}
void FIFO(char s[],char F[],int l,int f){
    int i,k,j=0,flag=0,cnt=0;
    printf("\n PAGE\t FAULTS\t\t FRAMES");
    for(i=0;i<l;i++){
        for(k=0;k<f;k++)if(F[k]==s[i])flag=1;
        printf("\n %c",s[i]);
        if(flag==0){
            F[j]=s[i];
            printf("\t Page-fault %d\t",cnt);
            j++; cnt++;
        }
        else{
            flag=0;
            printf("\t No Page-fault\t");
        }
        for(k=0;k<f;k++)printf(" %c",F[k]);
        if(j==f)j=0;
    }
}
void lru(char s[],char F[],int l,int f){
    int i,k,m,j=0,flag=0,cnt=0,top=0;
    printf("\n PAGE\t FAULTS\t\t FRAMES");
    for(i=0;i<l;i++){
        for(k=0;k<f;k++)if(F[k]==s[i]){flag=1; break;}
        printf("\n %c",s[i]);
        F[top]=s[i];
        if(j!=f && flag==0){
            j++; cnt++;
            if(j!=f)top++;
        }
        else if(flag==0){for(k=0;k<top;k++)F[k]=F[k+1]; cnt++;}
             else for(m=k;m<top;m++)F[m]=F[m+1]; 
        if(flag==0)printf("\t Page-fault %d\t",cnt);
        else printf("\t No page fault\t");
        for(k=0;k<f;k++)printf(" %c",F[k]);
        flag=0;
    }
}

    """)