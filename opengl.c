#include <SDL/SDL.h>
#include <SDL/SDL_opengl.h>

#include <stdio.h>

#include "demo.vsh.h"
#include "demo.fsh.h"

void setShaders() 
{
    
    GLuint v = glCreateShader(GL_VERTEX_SHADER);
    GLuint f = glCreateShader(GL_FRAGMENT_SHADER);	
    
    glShaderSource(v, 1, &vertexShader, NULL);
    glShaderSource(f, 1, &fragmentShader, NULL);
    
    glCompileShader(v);
    glCompileShader(f);
    
    GLuint p = glCreateProgram();
    
    glAttachShader(p,v);
    glAttachShader(p,f);
    
    glLinkProgram(p);
    glUseProgram(p);
}

int main(int argc, char **argv)
{
    if( SDL_Init( SDL_INIT_VIDEO ) != 0 )
    {
        printf("failed to init SDL.\n");
        return 1;
    }

    printf("success.\n");
    
    SDL_SetVideoMode( 800, 450, 32, SDL_OPENGL | SDL_FULLSCREEN );

    glDisable(GL_DEPTH_TEST);

    setShaders();
    
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

        glRecti(-1, -1, 1, 1);

        SDL_GL_SwapBuffers();
    }

    SDL_Quit();
    
    return 0;
}
