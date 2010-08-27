#include <SDL/SDL.h>
#include <SDL/SDL_opengl.h>

#include <stdio.h>

int main(int argc, char **argv)
{
    if( SDL_Init( SDL_INIT_VIDEO ) != 0 )
    {
        printf("failed to init SDL.\n");
        return 1;
    }

    printf("success.\n");
    
    SDL_SetVideoMode( 800, 450, 32, SDL_OPENGL | SDL_FULLSCREEN );
    
    while (1)
    {
        SDL_Event event;

        while( SDL_PollEvent(&event) )
        {
            switch(event.type)
            {
            case SDL_KEYDOWN:
            case SDL_QUIT:
                SDL_Quit();
                exit(0);
                break;
            default:
                break;
            }
        }

    }

    SDL_Quit();
    
    return 0;
}
