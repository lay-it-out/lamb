FROM nixos/nix
RUN bash -c 'echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf'
WORKDIR /work
COPY . /work
RUN nix develop --command bash -c 'echo Development environment is being built... (should not take over 5min)'
CMD nix develop
