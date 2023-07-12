FROM docker.io/nixos/nix
RUN bash -c 'echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf'
WORKDIR /work
COPY . /work
RUN nix develop --command echo 'Development environment built.' 
CMD nix develop
