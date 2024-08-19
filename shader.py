from pyglet.graphics.shader import Shader, ShaderProgram

# create vertex and fragment shader sources
vertex_source_default = """
#version 330
layout(location =0) in vec3 vertices;
layout(location =1) in vec4 colors;
layout(location =2) in vec3 normals; 
layout(location =3) in vec2 uvs;

out vec3 fragPos;
out vec4 fragColor;
out vec3 fragNormal;
out vec2 texCoords;
out float FogFactor; // Pass fog factor to fragment shader

// add a view-projection uniform and multiply it by the vertices
uniform mat4 view_proj;
uniform mat4 model;


// for fog
uniform float fogStart; // Fog start distance
uniform float fogEnd; // Fog end distance

void main()
{
    vec4 world = model * vec4(vertices, 1.0f);
    gl_Position = view_proj * world; // local->world->vp
    fragColor = colors;

    fragPos = vec3(world);
    fragNormal = transpose(inverse(mat3(model))) * normals;

    texCoords = uvs;

    float distance = length(world.xyz);
    FogFactor = (fogEnd - distance) / (fogEnd - fogStart);
    FogFactor = clamp(FogFactor, 0.0, 1.0);
}
"""

fragment_source_default = """
#version 330
in vec3 fragPos;
in vec4 fragColor;
in vec3 fragNormal;
in vec2 texCoords;
in float FogFactor;

out vec4 outColor;

uniform vec3 lightPos;
uniform vec3 viewPos;

uniform vec3 k_a;
uniform vec3 k_d;
uniform vec3 k_s;

uniform bool useTexture;
uniform sampler2D sampTexture;
uniform vec4 fogColor; // Fog color

void main()
{
    vec4 mixedColor;
    if (useTexture)
    {
        vec4 texturedColor = texture(sampTexture, texCoords) * fragColor;
        mixedColor = mix(fogColor, texturedColor, FogFactor);
    }
    else
    {
        // Mix the fragment color with the fog color based on the fog factor
        mixedColor = mix(fogColor, fragColor, FogFactor);
    }

    vec3 color = vec3(mixedColor);

    // ambient
    vec3 ambient = k_a * color;

    // diffuse
    vec3 lightDir = normalize(lightPos - fragPos);
    vec3 normal = normalize(fragNormal);

    float diff = max(dot(lightDir, normal), 0.0);
    vec3 diffuse = k_d * diff * color;

    // specular
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = k_s * spec;
    
    vec3 result = ambient + diffuse + specular;        
    outColor = vec4(result, 1.0);

}
"""

def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)